# 🎙️ PodClipper: Turn Podcasts into Viral Clips

A Streamlit web app that automatically finds the most engaging segments from long podcast episodes and turns them into shareable video clips using AssemblyAI. Here's a screenshot of the app after analyzing the Assembly Required series [episode](https://www.youtube.com/watch?v=DM3rgNM69Wg) with [Fireflies.ai](https://fireflies.ai/) CEO Krish Ramineni, where he talks with AssemblyAI CEO Dylan Fox about Fireflies' journey.

![PodClipper](app.png)

## 🚀 What it does

PodClipper helps you promote your podcasts on social media by:

- Analyzes your full podcast episode using AI
- Identifies the 3-5 most "clip-worthy" moments
- Creates ready-to-share video clips with captions
- Generates catchy titles for each clip
- All with zero editing skills required

## ⚙️ Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Rename `.env.example` and `.env` and add your [AssemblyAI API key](https://www.assemblyai.com/dashboard/signup):
   ```
   ASSEMBLYAI_API_KEY=your_api_key_here
   ```

3. Install FFmpeg (required for creating video clips):

   - **On Ubuntu/Debian:**
     ```bash
     sudo apt-get install ffmpeg
     ```
   
   - **On macOS (using Homebrew):**
     ```bash
     brew install ffmpeg
     ```
   
   - **On Windows:**
     Download and install from [FFmpeg website](https://ffmpeg.org/download.html)
     Add FFmpeg to your system PATH
     
   Note: The app can still analyze podcasts without FFmpeg, but won't be able to create video clips

## 🎯 Usage

Run the Streamlit app:

```bash
streamlit run main.py
```

Then in your browser:

1. Upload your podcast episode (MP3, MP4, WAV, or M4A)
2. Choose how many clips you want to generate
3. Set the desired duration for each clip
4. Click "Generate Viral Clips"
5. Download your clips and share them on social media!
