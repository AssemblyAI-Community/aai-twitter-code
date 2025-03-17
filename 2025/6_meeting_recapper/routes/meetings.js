import express from "express";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { AssemblyAI } from "assemblyai";
import { getDb } from "../models/database.js";

const router = express.Router();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const client = new AssemblyAI({
  apiKey: process.env.ASSEMBLYAI_API_KEY,
});

const uploadDir = path.join(__dirname, "..", "uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// Get all meetings
router.get("/", (req, res) => {
  const db = getDb();
  db.all("SELECT * FROM meetings ORDER BY created_at DESC", [], (err, rows) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    res.json(rows);
  });
});

// Get a specific meeting with all related data
router.get("/:id", (req, res) => {
  const db = getDb();
  const meetingId = req.params.id;

  db.get("SELECT * FROM meetings WHERE id = ?", [meetingId], (err, meeting) => {
    if (err) {
      return res.status(500).json({ error: err.message });
    }
    if (!meeting) {
      return res.status(404).json({ error: "Meeting not found" });
    }

    db.all(
      "SELECT * FROM speakers WHERE meeting_id = ?",
      [meetingId],
      (err, speakers) => {
        if (err) {
          return res.status(500).json({ error: err.message });
        }

        db.all(
          "SELECT * FROM segments WHERE meeting_id = ? ORDER BY start_time",
          [meetingId],
          (err, segments) => {
            if (err) {
              return res.status(500).json({ error: err.message });
            }

            db.all(
              "SELECT * FROM topics WHERE meeting_id = ? ORDER BY start_time",
              [meetingId],
              (err, topics) => {
                if (err) {
                  return res.status(500).json({ error: err.message });
                }

                db.all(
                  "SELECT * FROM action_items WHERE meeting_id = ?",
                  [meetingId],
                  (err, actionItems) => {
                    if (err) {
                      return res.status(500).json({ error: err.message });
                    }

                    res.json({
                      meeting,
                      speakers,
                      segments,
                      topics,
                      actionItems,
                    });
                  }
                );
              }
            );
          }
        );
      }
    );
  });
});

// Upload a meeting recording
router.post("/upload", async (req, res) => {
  try {
    if (!req.files || Object.keys(req.files).length === 0) {
      return res.status(400).json({ error: "No files were uploaded" });
    }

    const meetingFile = req.files.meeting;
    const title = req.body.title || "Untitled Meeting";

    // Create a unique filename
    const timestamp = Date.now();
    const filename = `${timestamp}_${meetingFile.name}`;
    const filePath = path.join(uploadDir, filename);

    await meetingFile.mv(filePath);

    const db = getDb();
    db.run(
      "INSERT INTO meetings (title, file_path) VALUES (?, ?)",
      [title, filePath],
      function (err) {
        if (err) {
          return res.status(500).json({ error: err.message });
        }

        const meetingId = this.lastID;

        processAudio(filePath, meetingId);

        res.json({
          id: meetingId,
          title,
          status: "processing",
          message: "File uploaded successfully and processing started",
        });
      }
    );
  } catch (error) {
    console.error("Upload error:", error);
    res.status(500).json({ error: error.message });
  }
});

// Process the audio with AssemblyAI
async function processAudio(filePath, meetingId) {
  try {
    const db = getDb();

    const transcript = await client.transcripts.transcribe({
      audio: filePath,
      speaker_labels: true,
      sentiment_analysis: true,
      auto_highlights: true,
      entity_detection: true,
      summarization: true,
    });

    db.run("UPDATE meetings SET transcript_id = ?, duration = ? WHERE id = ?", [
      transcript.id,
      transcript.audio_duration,
      meetingId,
    ]);

    // Process the transcript results and store in the database

    // 1. Store speaker data
    if (transcript.speaker_labels && transcript.utterances) {
      const speakerTimes = {};

      transcript.utterances.forEach((utterance) => {
        const speakerId = utterance.speaker;
        const duration = utterance.end - utterance.start;

        if (!speakerTimes[speakerId]) {
          speakerTimes[speakerId] = 0;
        }

        speakerTimes[speakerId] += duration;
      });

      Object.entries(speakerTimes).forEach(([speakerId, speakingTime]) => {
        db.run(
          "INSERT INTO speakers (meeting_id, speaker_id, speaking_time) VALUES (?, ?, ?)",
          [meetingId, speakerId, speakingTime]
        );
      });
    }

    // 2. Store segments with sentiment analysis
    if (transcript.sentiment_analysis_results) {
      transcript.sentiment_analysis_results.forEach((segment) => {
        db.run(
          "INSERT INTO segments (meeting_id, start_time, end_time, text, sentiment) VALUES (?, ?, ?, ?, ?)",
          [
            meetingId,
            segment.start,
            segment.end,
            segment.text,
            segment.sentiment_score,
          ]
        );
      });
    }

    // 3. Store detected topics
    if (
      transcript.auto_highlights_result &&
      transcript.auto_highlights_result.results
    ) {
      transcript.auto_highlights_result.results.forEach((highlight) => {
        db.run(
          "INSERT INTO topics (meeting_id, topic, start_time, end_time) VALUES (?, ?, ?, ?)",
          [
            meetingId,
            highlight.text,
            highlight.timestamps[0].start,
            highlight.timestamps[0].end,
          ]
        );
      });
    }

    // 4. Use LeMUR to identify action items
    const actionItemsPrompt = `
      Analyze this meeting transcript and identify all action items.
      For each action item, provide:
      1. The action item text
      2. The person assigned to it (if mentioned)
      3. Any deadlines or due dates mentioned
      Format as JSON array with fields: text, assignee, deadline, timeIndex
      
      Example format:
      [
        {
          "text": "Update the metrics dashboard",
          "assignee": "Eric",
          "deadline": "next Friday",
          "timeIndex": 450
        }
      ]
      
      If any information is not available (like assignee or deadline), return null for that field.

      IMPORTANT: DO NOT INCLUDE A PREAMBLE. IMMEDIATELY START WITH THE JSON ARRAY.
    `;

    try {
      const lemurResponse = await client.lemur.task({
        transcript_ids: [transcript.id],
        prompt: actionItemsPrompt,
        final_model: "anthropic/claude-3-5-sonnet", // Using Claude 3.5 Sonnet model with correct format
      });

      let actionItems = [];

      try {
        // Attempt to parse the JSON response
        actionItems = JSON.parse(lemurResponse.response);

        // If the response isn't an array, wrap it in one
        if (!Array.isArray(actionItems)) {
          console.warn(
            "LeMUR response was not an array, attempting to normalize"
          );
          if (typeof actionItems === "object") {
            actionItems = [actionItems];
          } else {
            throw new Error("Could not parse LeMUR response as action items");
          }
        }
      } catch (parseError) {
        console.error("Error parsing LeMUR response:", parseError);
        console.log("Raw LeMUR response:", lemurResponse.response);

        // Fallback: try to extract using regex if JSON parsing fails
        // This is a simple fallback and might not work for all cases
        const regex =
          /"text"\s*:\s*"([^"]+)"[^}]*"assignee"\s*:\s*"?([^",}]*)"?[^}]*"deadline"\s*:\s*"?([^",}]*)"?[^}]*"timeIndex"\s*:\s*(\d+)/g;
        let match;
        actionItems = [];

        while ((match = regex.exec(lemurResponse.response)) !== null) {
          actionItems.push({
            text: match[1],
            assignee: match[2] || null,
            deadline: match[3] || null,
            timeIndex: parseInt(match[4], 10) || 0,
          });
        }

        if (actionItems.length === 0) {
          console.warn(
            "Could not extract action items from LeMUR response, using empty list"
          );
        }
      }

      for (const item of actionItems) {
        if (item && item.text) {
          const assignee = item.assignee || null;
          const startTime = item.timeIndex || 0;

          db.run(
            "INSERT INTO action_items (meeting_id, text, assignee, start_time) VALUES (?, ?, ?, ?)",
            [meetingId, item.text, assignee, startTime]
          );
        }
      }

      console.log("LeMUR processing completed successfully");
    } catch (lemurError) {
      console.error("Error with LeMUR processing:", lemurError);
    }

    console.log(`Processing completed for meeting ID: ${meetingId}`);
  } catch (error) {
    console.error("Error processing audio:", error);
  }
}

export default router;
