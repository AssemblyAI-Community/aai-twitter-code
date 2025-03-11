# 🐦 Audio-to-Tweet Generator

A Streamlit app that uses AssemblyAI to automatically generate tweet-sized summaries from audio and video content.

![App Screenshot](app.png)

## 🚀 Features

- Upload any audio or video file
- Automatically extract tweetable highlights from your content
- Generate chapter summaries as ready-to-share tweets
- One-click tweet download for easy sharing

## ⚙️ Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Rename `.env.example` as `.env` file, and add your [AssemblyAI API key](https://www.assemblyai.com/dashboard/signup):
   ```
   ASSEMBLYAI_API_KEY=your_api_key_here
   ```

## 🎯 Usage

1. Run the Streamlit app:
   ```
   streamlit run main.py
   ```

2. Open your browser and go to `http://localhost:8501`

3. Upload an audio or video file

4. Click "Generate Tweets"

5. Copy your favorite tweets or download them all
