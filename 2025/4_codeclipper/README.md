# CodeClipper

![CodeClipper](app.png)

**Extract key concepts and practical code examples from lengthy programming tutorials**

CodeClipper is a Streamlit web application that uses AI to analyze coding tutorials and extract the most educational segments, it easy to clip and share your coding tutorials. The screenshot above shows the app used to clip our tutorial on [building an AI agent with LiveKit and Python](https://www.youtube.com/watch?v=A400nCCZlK4)

Follow [AssemblyAI's Twitter account](https://x.com/AssemblyAI) for more cool projects like this

## Features

- **AI-Powered Code Concept Extraction**: Identifies the most valuable educational segments from coding tutorials
- **Smart Concept Recognition**: Focuses on practical code examples, implementations, and clear explanations
- **Downloadable Clips**: Save key concept clips to build your personal programming knowledge base
- **Technology Tagging**: Automatically identifies programming languages and frameworks discussed

## Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory and add your [AssemblyAI API key](https://www.assemblyai.com/dashboard/signup):
   ```
   ASSEMBLYAI_API_KEY=your_api_key_here
   ```

3. Run the Streamlit app:
   ```
   streamlit run main.py
   ```

## Requirements

- Python 3.7+
- FFmpeg
- AssemblyAI API key

## How It Works

1. **Input**: Upload a tutorial video
2. **Transcription**: AssemblyAI transcribes the audio content
3. **Concept Identification**: AI analyzes the transcript to identify key coding concepts and practical examples
4. **Clip Extraction**: FFmpeg extracts video segments containing the identified concepts
5. **Review and Download**: Watch and download the concept clips