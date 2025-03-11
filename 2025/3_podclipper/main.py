#!/usr/bin/env python3
"""
PodcastClipper: Turn long podcast episodes into viral short clips
Uses AssemblyAI to find the most engaging moments from any podcast 
and generates ready-to-share video clips with captions.
"""

import assemblyai as aai
import streamlit as st
import tempfile
from pathlib import Path
import os
import shutil
import subprocess
import re
from typing import List, Dict, Union, Optional, Tuple, Any
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("ASSEMBLYAI_API_KEY")
if not api_key:
    st.error("⚠️ No AssemblyAI API key found. Please set ASSEMBLYAI_API_KEY in your .env file.")
else:
    aai.settings.api_key = api_key

st.set_page_config(page_title="PodcastClipper", page_icon="🎙️")


def parse_timestamp(timestamp: str) -> float:
    """Convert a timestamp string (HH:MM:SS) to seconds"""
    timestamp = timestamp.strip()
    timestamp = re.sub(r'[^\d:]', '', timestamp)
    
    if not timestamp:
        return 0
    
    parts = timestamp.split(':')
    try:
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
        else:
            return float(parts[0])
    except (ValueError, IndexError):
        st.warning(f"Could not parse timestamp: {timestamp}. Using 0:00 instead.")
        return 0


def get_highlights(audio_file: str, num_clips: int = 3, clip_duration: int = 60) -> Tuple[str, List, str]:
    """Extract the most interesting clips from the podcast using AssemblyAI"""
    transcriber = aai.Transcriber()
    
    with st.status("Transcribing podcast...") as status:
        transcript = transcriber.transcribe(audio_file)
        status.update(label="Finding the most engaging moments...")
        
        # Use LeMUR to find the most interesting parts
        highlights_prompt = f"""
        Find the {num_clips} most interesting, quotable, or 'clip-worthy' segments in this podcast.
        Each segment should be around {clip_duration} seconds long and be able to stand alone as an engaging clip.
        For each segment, provide:
        1. The timestamp where the clip should start
        2. A catchy title for the clip (60 characters max)
        3. A one-sentence summary of why this clip is interesting
        
        Only include segments that would be engaging out of context and make viewers want to share the clip.
        """
        
        highlights = transcript.lemur.task(
            highlights_prompt,
            final_model=aai.LemurModel.claude3_haiku
        )
        
        words = transcript.words
        
        return highlights.response, words, transcript.text


def create_clip(video_file: str, start_time: str, duration: int, title: str, words: List) -> str:
    """Create a short clip using FFmpeg (no ImageMagick required)"""
    start_seconds = parse_timestamp(start_time)
    
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        output_path = tmp.name
    
    try:
        cmd = [
            "ffmpeg", "-i", video_file,
            "-ss", str(start_seconds),
            "-t", str(duration),
            "-c:v", "libx264", "-c:a", "aac",
            "-strict", "experimental",
            "-b:a", "192k",
            "-y", output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        st.error(f"Error creating clip: {e}")
        shutil.copy(video_file, output_path)
        return output_path


def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed on the system."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        st.warning("FFmpeg not found. Will analyze content but can't create video clips. Please install FFmpeg.")
        return False


def extract_clip_info(sections: List[str]) -> List[Dict[str, str]]:
    """Extract clip information from the highlights text"""
    clips_info = []
    
    for section in sections:
        if not section.strip():
            continue
        
        lines = section.strip().split("\n")
        if len(lines) >= 2:
            timestamp_line = [l for l in lines if ":" in l and ("start" in l.lower() or "timestamp" in l.lower())]
            title_line = [l for l in lines if "title" in l.lower() or ":" in l]
            summary_line = [l for l in lines if "summary" in l.lower() or "why" in l.lower()]
            
            if timestamp_line and title_line:
                timestamp = timestamp_line[0].split(":", 1)[1].strip()
                title = title_line[0].split(":", 1)[1].strip()
                summary = ""
                if summary_line:
                    summary = summary_line[0].split(":", 1)[1].strip() if ":" in summary_line[0] else summary_line[0]
                
                clips_info.append({
                    "timestamp": timestamp,
                    "title": title,
                    "summary": summary
                })
    
    return clips_info


def display_clips(temp_path: str, clips_info: List[Dict[str, str]], clip_duration: int, 
                  ffmpeg_installed: bool, words: List) -> None:
    """Display the generated clips or transcript excerpts"""
    
    for i, clip_info in enumerate(clips_info):
        timestamp = clip_info["timestamp"]
        title = clip_info["title"]
        summary = clip_info["summary"]
        
        st.markdown(f"### Clip {i+1}: {title}")
        if summary:
            st.markdown(f"*{summary}*")
        
        if ffmpeg_installed:
            clip_path = create_clip(temp_path, timestamp, clip_duration, title, words)
            st.video(clip_path)
            
            with open(clip_path, "rb") as file:
                st.download_button(
                    label=f"Download Clip {i+1}",
                    data=file,
                    file_name=f"viral_clip_{i+1}.mp4",
                    mime="video/mp4"
                )
        else:
            start_seconds = parse_timestamp(timestamp)
            st.info(f"Start time: {timestamp} (Would create a {clip_duration}s clip)")
            
            clip_transcript = " ".join([w.text for w in words 
                                      if start_seconds <= w.start/1000 <= start_seconds + clip_duration])
            st.text_area(f"Clip {i+1} Transcript", clip_transcript, height=100)


def process_podcast(file_path: str, num_clips: int, clip_duration: int) -> None:
    """Process a podcast file to find and extract interesting clips."""
    ffmpeg_installed = check_ffmpeg_installed()
    
    try:
        highlights, words, full_transcript = get_highlights(file_path, num_clips, clip_duration)
        
        st.markdown("## 🔥 Your Viral Clips")
        st.text_area("Full analysis", highlights, height=200)
        
        sections = highlights.split("\n\n")
        clips_info = extract_clip_info(sections)
        
        display_clips(file_path, clips_info, clip_duration, ffmpeg_installed, words)
        
    except Exception as e:
        st.error(f"Error processing podcast: {str(e)}")
        import traceback
        st.error(traceback.format_exc())


def main() -> None:
    """Main application entry point"""
    st.title("🎙️ PodcastClipper")
    st.subheader("Turn podcasts into viral short clips")
    
    uploaded_file = st.file_uploader("Upload podcast audio or video file", type=["mp3", "mp4", "wav", "m4a"])
    
    col1, col2 = st.columns(2)
    with col1:
        num_clips = st.slider("Number of clips to generate", 1, 5, 3)
    with col2:
        clip_duration = st.slider("Clip duration (seconds)", 30, 120, 60)
    
    if uploaded_file and st.button("✨ Generate Viral Clips"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            temp_path = tmp.name
        
        process_podcast(temp_path, num_clips, clip_duration)
        
        try:
            os.remove(temp_path)
        except OSError:
            pass
    
    st.markdown("""
    ---
    ### 🚀 How It Works
    1. Upload any podcast episode (audio or video)
    2. AI analyzes the content to find the most engaging moments
    3. Get ready-to-share clips with catchy titles
    4. Download and post to Twitter, TikTok, Instagram, etc.
    
    Powered by AssemblyAI and Streamlit
    """)


if __name__ == "__main__":
    main()