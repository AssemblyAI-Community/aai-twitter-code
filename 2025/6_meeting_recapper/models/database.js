import sqlite3 from "sqlite3";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const dataDir = path.join(__dirname, "..", "data");
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir);
}

const dbPath = path.join(dataDir, "meetings.db");

// Connect to the database
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error("Error connecting to database:", err.message);
  } else {
    console.log("Connected to SQLite database");
  }
});

// Initialize the database with necessary tables
function initDatabase() {
  db.serialize(() => {
    // Meetings table
    db.run(`CREATE TABLE IF NOT EXISTS meetings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      file_path TEXT,
      transcript_id TEXT,
      duration INTEGER,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);

    // Speakers table for speaker diarization data
    db.run(`CREATE TABLE IF NOT EXISTS speakers (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      meeting_id INTEGER,
      speaker_id TEXT,
      speaking_time INTEGER,
      FOREIGN KEY (meeting_id) REFERENCES meetings (id)
    )`);

    // Segments table for timeline data
    db.run(`CREATE TABLE IF NOT EXISTS segments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      meeting_id INTEGER,
      start_time INTEGER,
      end_time INTEGER,
      speaker_id TEXT,
      text TEXT,
      sentiment REAL,
      FOREIGN KEY (meeting_id) REFERENCES meetings (id)
    )`);

    // Topics table
    db.run(`CREATE TABLE IF NOT EXISTS topics (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      meeting_id INTEGER,
      topic TEXT,
      start_time INTEGER,
      end_time INTEGER,
      FOREIGN KEY (meeting_id) REFERENCES meetings (id)
    )`);

    // Action items table
    db.run(`CREATE TABLE IF NOT EXISTS action_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      meeting_id INTEGER,
      text TEXT,
      assignee TEXT,
      start_time INTEGER,
      FOREIGN KEY (meeting_id) REFERENCES meetings (id)
    )`);
  });
}

function getDb() {
  return db;
}

function closeDb() {
  db.close((err) => {
    if (err) {
      console.error("Error closing database:", err.message);
    } else {
      console.log("Database connection closed");
    }
  });
}

export { initDatabase, getDb, closeDb };
