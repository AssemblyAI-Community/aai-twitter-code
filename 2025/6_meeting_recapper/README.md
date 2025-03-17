# Meeting Visualizer

A web application that uses the AssemblyAI API to analyze meeting recordings and visualize speaker ratios, sentiment, and key topics.

![Meeting page](meeting.png)

![Upload page](upload.png)

## Features

- **Upload Meeting Recordings**: Upload audio or video files of meetings
- **Speaker Distribution**: Visualize speaking percentage for each participant
- **Sentiment Timeline**: Track sentiment changes throughout the meeting
- **Topic Timeline**: Automatically detect topics of discussion and rank them by relevance
- **Action Items**: [Automatically extract action items](https://www.assemblyai.com/blog/summarize-meetings-llms-python) from the meeting

## Technology Stack

- **Backend**: Node.js, Express
- **Speech Understanding**: AssemblyAI for [Speech-to-Text](https://www.assemblyai.com/products/speech-to-text) and [Speech Understanding](https://www.assemblyai.com/products/speech-understanding)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Visualizations**: D3.js

## Running the program

You need Node.js installed and an AssemblyAI API key, then:

1. Install dependencies:
   ```
   npm install
   ```

2. Rename `.env.example` to `.env` and add your AssemblyAI API key:
   ```
   ASSEMBLYAI_API_KEY=your_api_key_here
   ```

3. Start the application
   ```
   npm start
   ```

4. Access the application by opening your browser and navigate to `http://localhost:3000`


## Directory Structure

```
meeting-visualizer/
├── app.js                # Main application file
├── data/
│   └── meetings.db       # Local SQLite database
├── models/
│   └── database.js       # Database setup and operations
├── routes/
│   └── meetings.js       # API routes
├── public/               # Frontend files
│   ├── index.html        # Main HTML page
│   ├── css/
│   │   └── style.css     # Styles
│   └── js/
│       └── main.js       # Frontend JavaScript
├── uploads/              # Uploaded audio/video files
└── .env                  # Environment variables
```