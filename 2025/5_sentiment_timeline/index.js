import dotenv from 'dotenv';
import fs from 'fs/promises';
import { AssemblyAI } from 'assemblyai';

dotenv.config();

const API_KEY = process.env.ASSEMBLYAI_API_KEY;
if (!API_KEY) {
  console.error('⚠️ Please set ASSEMBLYAI_API_KEY in your .env file');
  process.exit(1);
}

const client = new AssemblyAI({
  apiKey: API_KEY
});

async function analyzeSentiment(audioUrl) {
  try {
    console.log(`🎙️ Creating transcription request for: ${audioUrl}`);
    
    // Create transcription with sentiment analysis
    const transcript = await client.transcripts.transcribe({
      audio: audioUrl,
      sentiment_analysis: true
    });
    
    console.log(`✅ Transcription complete: ${transcript.id}`);
    return transcript;
  } catch (err) {
    console.error('❌ API Error:', err.message);
    throw err;
  }
}

function createSentimentTimeline(transcript) {
  // Map sentiment scores to timestamps
  return transcript.sentiment_analysis_results.map(result => {
    let score;
    if (result.sentiment === 'POSITIVE') {
      score = 1;
    } else if (result.sentiment === 'NEUTRAL') {
      score = 0;
    } else if (result.sentiment === 'NEGATIVE') {
      score = -1;
    } else {
      // Throw error for unexpected sentiment values
      throw new Error(`Unexpected sentiment value encountered: ${result.sentiment}`);
    }
    
    return {
      time: Math.floor(result.start / 1000), // Time in seconds
      text: result.text.substring(0, 50) + (result.text.length > 50 ? '...' : ''),
      sentiment: result.sentiment,
      score: score
    };
  });
}

async function saveTimeline(timeline, filename = 'sentiment-timeline.json') {
  await fs.writeFile(filename, JSON.stringify(timeline, null, 2));
  console.log(`💾 Results saved to ${filename}`);
}

async function main() {
  try {
    const audioUrl = process.argv[2];
    if (!audioUrl) {
      console.error('⚠️ Usage: node index.js <audio_url>');
      process.exit(1);
    }
    
    console.log(`🚀 Analyzing sentiment in: ${audioUrl}`);
    const transcript = await analyzeSentiment(audioUrl);
    
    if (!transcript.sentiment_analysis_results || transcript.sentiment_analysis_results.length === 0) {
      console.log('⚠️ No sentiment data found in transcript');
      process.exit(0);
    }
    
    const timeline = createSentimentTimeline(transcript);
    
    console.log(`✅ Found ${timeline.length} sentiment segments`);
    await saveTimeline(timeline);
    
    console.log('\n📊 Sentiment Journey Preview:');
    timeline.slice(0, 3).forEach(item => {
      const emoji = item.score === -1 ? '😔' : item.score === 0 ? '😐' : '😊';
      console.log(`${emoji} [${item.time}s]: ${item.text}`);
    });
    console.log('...');
  } catch (err) {
    console.error('❌ Error:', err.message);
    process.exit(1);
  }
}

main();