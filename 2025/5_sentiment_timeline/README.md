# Sentiment Timeline

![Sentiment Timeline](app.png)

**Visualize the emotional journey throughout any audio content**

Sentiment Timeline is a simple Node.js tool that uses AssemblyAI to analyze the emotional tone throughout podcasts, speeches, interviews, or any audio content. It creates a timeline of sentiment changes over time for audio and video files in the terminal and saves it to a JSON file.

## Installation

You'll need to have Node.js installed and an AssemblyAI API key, then:

1. Install dependencies:
   ```
   npm install
   ```

2. Rename `.env.example` to `.env` and add your AssemblyAI API key:
   ```
   ASSEMBLYAI_API_KEY=your_api_key_here
   ```

## Usage

Run the tool with a publicly-accessible download URL or local file of your choice
```bash
npm start https://example.com/your-audio-file.mp3
npm start ./your/local/file.mp3
```
Try out this sample audio file, which was used to generate the example JSON file in the directory:
```bash
npm start https://storage.googleapis.com/aai-web-samples/world_news_this_week_2023_06_30.mp3
```

The tool will:
1. Send the audio URL to AssemblyAI for processing
2. Analyze the content for sentiment
3. Create a sentiment timeline
4. Save results to `sentiment-timeline.json`
5. Display a preview of findings

## Example Output

```json
[
  {
    "time": 1,
    "text": "From ABC News, World News this Week.",
    "sentiment": "NEUTRAL",
    "score": 0
  },
  {
    "time": 11,
    "text": "I'm Chuck Seberson in New York.",
    "sentiment": "NEUTRAL",
    "score": 0
  },
  {
    "time": 13,
    "text": "Coming up, the Supreme Court strikes that down.",
    "sentiment": "NEUTRAL",
    "score": 0
  },
  // ...
]
```