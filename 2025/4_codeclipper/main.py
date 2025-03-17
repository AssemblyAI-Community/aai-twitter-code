#!/usr/bin/env python3
"""
CodeClipper: Extract key concepts and practical code examples from lengthy programming tutorials
Uses AssemblyAI to identify the most educational segments and generates ready-to-share clips.
"""

import assemblyai as aai
import streamlit as st
import tempfile
from pathlib import Path
import os
import subprocess
import re
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv
import json
import time

# Page configuration
st.set_page_config(page_title="CodeClipper", page_icon="💻")

# Load environment variables
load_dotenv()
api_key = os.getenv("ASSEMBLYAI_API_KEY")
if not api_key:
    st.error("⚠️ No AssemblyAI API key found. Please set ASSEMBLYAI_API_KEY in your .env file.")
    st.stop()
else:
    aai.settings.api_key = api_key

# Initialize session state
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'clips_info' not in st.session_state:
    st.session_state.clips_info = []
if 'transcript_text' not in st.session_state:
    st.session_state.transcript_text = ""
if 'words' not in st.session_state:
    st.session_state.words = []
if 'concepts_analysis' not in st.session_state:
    st.session_state.concepts_analysis = ""
if 'clip_paths' not in st.session_state:
    st.session_state.clip_paths = []
if 'error_log' not in st.session_state:
    st.session_state.error_log = []


def parse_timestamp(timestamp: str) -> Optional[float]:
    """
    Convert a timestamp string to seconds with robust error handling
    
    Parameters:
        timestamp (str): Timestamp in format HH:MM:SS, MM:SS, or SS
        
    Returns:
        float: Time in seconds or None if parsing fails
    """
    # Clean the timestamp string
    timestamp = timestamp.strip()
    
    # First try to extract timestamp from text using regex
    match = re.search(r'(\d+:)?(\d+:)?(\d+)', timestamp)
    if not match:
        return None
    
    timestamp = match.group(0)
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
        return None


def run_command(cmd: List[str], error_msg: str) -> Tuple[bool, str]:
    """
    Run a shell command with proper error handling
    
    Parameters:
        cmd (List[str]): Command and arguments
        error_msg (str): Error message prefix
        
    Returns:
        Tuple[bool, str]: Success status and error message if any
    """
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        return True, ""
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        details = str(e)
        if hasattr(e, 'stderr') and e.stderr:
            details += f"\nDetails: {e.stderr.decode('utf-8', errors='replace')}"
        return False, f"{error_msg}: {details}"


def check_ffmpeg_installed() -> bool:
    """
    Check if FFmpeg is installed and available
    
    Returns:
        bool: True if FFmpeg is available, False otherwise
    """
    success, _ = run_command(["ffmpeg", "-version"], "FFmpeg not found")
    if not success:
        st.warning("FFmpeg not found. Will analyze content but can't create video clips. Please install FFmpeg.")
    return success


def extract_audio(video_path: str) -> Tuple[Optional[str], str]:
    """
    Extract audio from video using FFmpeg
    
    Parameters:
        video_path (str): Path to the video file
        
    Returns:
        Tuple[Optional[str], str]: Path to extracted audio file and error message if any
    """
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
        audio_path = tmp.name
    
    cmd = [
        "ffmpeg", "-i", video_path,
        "-q:a", "0", "-map", "a",
        "-y", audio_path
    ]
    
    success, error = run_command(cmd, "Error extracting audio")
    if not success:
        st.session_state.error_log.append(error)
        return None, error
    
    return audio_path, ""


def get_code_concepts(audio_file: str, num_clips: int = 3, clip_duration: int = 60) -> Tuple[str, List, str]:
    """
    Extract the most educational code concepts from the tutorial using AssemblyAI
    
    Parameters:
        audio_file (str): Path to audio file
        num_clips (int): Number of clips to extract
        clip_duration (int): Duration of each clip in seconds
        
    Returns:
        Tuple[str, List, str]: AI analysis, word timings, and full transcript
    """
    transcriber = aai.Transcriber()
    
    # Transcribe the audio
    transcript = transcriber.transcribe(audio_file)
    
    # Use LeMUR to find the most educational parts with structured output request
    concepts_prompt = f"""
    Find the {num_clips} most educational, practical code examples or explanations in this programming tutorial.
    Each segment should be around {clip_duration} seconds long and demonstrate a clear coding concept.
    
    Format your response as a valid JSON array, where each object has these exact fields:
    - "timestamp": The exact timestamp where the clip should start (in MM:SS format)
    - "title": A descriptive title for the code concept (60 characters max)
    - "technology": The programming language or framework being demonstrated
    - "summary": A one-sentence summary of what developers will learn
    
    Make sure the timestamps are accurate and exist in the transcript.
    Ensure each clip covers a different concept and is spaced sufficiently apart in the video.
    Pick segments with clear explanations of working code and practical implementation.
    """
    
    concepts = transcript.lemur.task(
        concepts_prompt,
        final_model=aai.LemurModel.claude3_haiku
    )
    
    words = transcript.words
    
    return concepts.response, words, transcript.text


def create_clip(video_file: str, start_time: float, duration: int) -> Tuple[Optional[str], str]:
    """
    Create a short clip using FFmpeg
    
    Parameters:
        video_file (str): Path to the video file
        start_time (float): Start time in seconds
        duration (int): Clip duration in seconds
        
    Returns:
        Tuple[Optional[str], str]: Path to the created clip and error message if any
    """
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
        output_path = tmp.name
    
    cmd = [
        "ffmpeg", "-i", video_file,
        "-ss", str(start_time),
        "-t", str(duration),
        "-c:v", "libx264", "-c:a", "aac",
        "-strict", "experimental",
        "-b:a", "192k",
        "-y", output_path
    ]
    
    success, error = run_command(cmd, "Error creating clip")
    if not success:
        st.session_state.error_log.append(error)
        return None, error
    
    return output_path, ""


def extract_clip_info(concepts_text: str) -> List[Dict[str, str]]:
    """
    Extract clip information from the concepts text with robust parsing
    
    Parameters:
        concepts_text (str): Text response from AI analysis
        
    Returns:
        List[Dict[str, str]]: List of clip information dictionaries
    """
    # First try to parse as JSON
    try:
        # Check if there's a JSON array in the text
        match = re.search(r'\[\s*\{.*\}\s*\]', concepts_text, re.DOTALL)
        if match:
            clips_info = json.loads(match.group(0))
            if isinstance(clips_info, list) and all(isinstance(item, dict) for item in clips_info):
                # Ensure all required fields are present
                required_fields = ["timestamp", "title", "technology", "summary"]
                valid_clips = []
                for clip in clips_info:
                    if all(field in clip for field in required_fields):
                        valid_clips.append(clip)
                if valid_clips:
                    return valid_clips
    except json.JSONDecodeError:
        pass
    
    # Fallback to regex parsing if JSON parsing fails
    clips_info = []
    sections = concepts_text.split("\n\n")
    
    for section in sections:
        if not section.strip():
            continue
        
        # Extract information using regex patterns
        timestamp_match = re.search(r'timestamp:?\s*([0-9:]+)', section, re.IGNORECASE)
        title_match = re.search(r'title:?\s*([^\n]+)', section, re.IGNORECASE)
        tech_match = re.search(r'technology:?\s*([^\n]+)', section, re.IGNORECASE) or \
                     re.search(r'language:?\s*([^\n]+)', section, re.IGNORECASE) or \
                     re.search(r'framework:?\s*([^\n]+)', section, re.IGNORECASE)
        summary_match = re.search(r'summary:?\s*([^\n]+)', section, re.IGNORECASE)
        
        if timestamp_match:
            clip_info = {
                "timestamp": timestamp_match.group(1).strip(),
                "title": title_match.group(1).strip() if title_match else "Untitled Clip",
                "technology": tech_match.group(1).strip() if tech_match else "Unknown",
                "summary": summary_match.group(1).strip() if summary_match else ""
            }
            clips_info.append(clip_info)
    
    return clips_info


def validate_clips_info(clips_info: List[Dict[str, str]], num_clips: int, video_duration: float) -> List[Dict[str, str]]:
    """
    Validate and fix clip information
    
    Parameters:
        clips_info (List[Dict[str, str]]): List of clip information
        num_clips (int): Expected number of clips
        video_duration (float): Duration of the video in seconds
        
    Returns:
        List[Dict[str, str]]: Validated clip information
    """
    valid_clips = []
    
    # Ensure we have the requested number of clips
    if len(clips_info) < num_clips:
        st.warning(f"Only found {len(clips_info)} clips instead of the requested {num_clips}")
    
    for i, clip in enumerate(clips_info):
        # Parse timestamp
        start_time = parse_timestamp(clip["timestamp"])
        
        # Skip invalid clips or add default timestamp
        if start_time is None:
            # Create a fallback timestamp based on video length and position
            fallback_time = (i * video_duration) / (min(len(clips_info) + 1, num_clips + 1))
            start_time = fallback_time
            clip["timestamp"] = f"{int(start_time // 60):02d}:{int(start_time % 60):02d}"
            st.warning(f"Fixed invalid timestamp for clip '{clip['title']}'")
        
        # Ensure clips don't run past the end of the video
        if start_time >= video_duration:
            start_time = max(0, video_duration - 60)
            clip["timestamp"] = f"{int(start_time // 60):02d}:{int(start_time % 60):02d}"
        
        # Store parsed seconds for later use
        clip["start_seconds"] = start_time
        valid_clips.append(clip)
    
    # Ensure clips are sufficiently spaced apart (minimum 20 seconds between clips)
    valid_clips.sort(key=lambda x: x["start_seconds"])
    for i in range(1, len(valid_clips)):
        prev_start = valid_clips[i-1]["start_seconds"]
        curr_start = valid_clips[i]["start_seconds"]
        
        if curr_start - prev_start < 20:
            # Adjust the current clip to be at least 20 seconds after the previous one
            new_start = prev_start + 20
            valid_clips[i]["start_seconds"] = new_start
            valid_clips[i]["timestamp"] = f"{int(new_start // 60):02d}:{int(new_start % 60):02d}"
    
    return valid_clips


def get_video_duration(video_path: str) -> float:
    """
    Get the duration of a video file
    
    Parameters:
        video_path (str): Path to the video file
        
    Returns:
        float: Duration in seconds or 0 if unable to determine
    """
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
        return float(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        # Default to a reasonable length if we can't determine
        return 600.0  # 10 minutes


def process_tutorial(file_path: str, num_clips: int, clip_duration: int) -> None:
    """
    Process a tutorial video to find and extract key code concepts
    
    Parameters:
        file_path (str): Path to the video file
        num_clips (int): Number of clips to extract
        clip_duration (int): Duration of each clip in seconds
    """
    # Reset session state for new processing
    st.session_state.processed = False
    st.session_state.clips_info = []
    st.session_state.clip_paths = []
    st.session_state.error_log = []
    
    # Check for FFmpeg
    ffmpeg_installed = check_ffmpeg_installed()
    
    try:
        # Get video duration
        video_duration = get_video_duration(file_path)
        
        # Extract audio for transcription
        with st.status("Extracting audio...") as status:
            audio_path, error = extract_audio(file_path)
            if not audio_path:
                st.error(f"Failed to extract audio: {error}")
                return
        
        # Transcribe and analyze
        with st.status("Transcribing and analyzing tutorial...") as status:
            concepts_text, words, full_transcript = get_code_concepts(audio_path, num_clips, clip_duration)
            
            # Parse the analysis
            clips_info = extract_clip_info(concepts_text)
            
            # Validate and fix clip information
            clips_info = validate_clips_info(clips_info, num_clips, video_duration)
            
            # Store in session state
            st.session_state.concepts_analysis = concepts_text
            st.session_state.words = words
            st.session_state.transcript_text = full_transcript
            st.session_state.clips_info = clips_info
            st.session_state.processed = True
        
        # Process video clips if FFmpeg is available
        if ffmpeg_installed:
            with st.status("Creating video clips...") as status:
                for i, clip_info in enumerate(clips_info):
                    status.update(label=f"Creating clip {i+1} of {len(clips_info)}...")
                    
                    # Create the clip
                    start_seconds = clip_info["start_seconds"]
                    clip_path, error = create_clip(file_path, start_seconds, clip_duration)
                    
                    if clip_path:
                        # Read and store clip data
                        with open(clip_path, "rb") as file:
                            st.session_state[f"clip_data_{i}"] = file.read()
                        st.session_state.clip_paths.append(clip_path)
                    else:
                        st.warning(f"Failed to create clip {i+1}: {error}")
                
                status.update(label="All clips processed!", state="complete")
        
        # Clean up temp files
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
        except (OSError, TypeError):
            pass
            
    except Exception as e:
        st.error(f"Error processing tutorial: {str(e)}")
        import traceback
        st.session_state.error_log.append(traceback.format_exc())
        return


def display_results():
    """Display the processed results"""
    if not st.session_state.processed or not st.session_state.clips_info:
        return
    
    st.markdown("## 💻 Your Code Concept Clips")
    
    # Display AI analysis with toggle
    with st.expander("View AI Analysis"):
        st.text_area("Full analysis", st.session_state.concepts_analysis, height=200)
    
    # Display clips
    for i, clip_info in enumerate(st.session_state.clips_info):
        title = clip_info["title"]
        technology = clip_info["technology"]
        summary = clip_info["summary"]
        timestamp = clip_info["timestamp"]
        
        # Create a nice card-like layout for each clip
        st.markdown(f"""
        <div style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 20px;">
            <h3>Clip {i+1}: {title}</h3>
            <p><strong>Technology:</strong> {technology}</p>
            <p><strong>Summary:</strong> {summary}</p>
            <p><strong>Starts at:</strong> {timestamp}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show video if available
        if i < len(st.session_state.clip_paths) and os.path.exists(st.session_state.clip_paths[i]):
            # Display the video
            try:
                st.video(st.session_state.clip_paths[i])
                
                # Download button using stored data
                if f"clip_data_{i}" in st.session_state:
                    sanitized_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
                    st.download_button(
                        label=f"Download Clip {i+1}",
                        data=st.session_state[f"clip_data_{i}"],
                        file_name=f"{sanitized_title}_{i+1}.mp4",
                        mime="video/mp4",
                        key=f"download_btn_{i}"
                    )
            except Exception as e:
                st.error(f"Error displaying clip {i+1}: {str(e)}")
        else:
            # If video not available, show transcript for that segment
            start_seconds = clip_info.get("start_seconds", parse_timestamp(timestamp) or 0)
            
            # Generate transcript for this clip
            clip_words = [w for w in st.session_state.words 
                          if start_seconds <= w.start/1000 < start_seconds + st.session_state.clip_duration]
            
            if clip_words:
                clip_transcript = " ".join(w.text for w in clip_words)
                st.text_area(f"Clip {i+1} Transcript", clip_transcript, height=100)
            else:
                st.warning(f"No transcript available for clip {i+1}")
    
    # Show errors if any occurred
    if st.session_state.error_log:
        with st.expander("View Error Log"):
            for error in st.session_state.error_log:
                st.error(error)


def main():
    """Main application entry point"""
    st.title("💻 CodeClipper")
    st.subheader("Extract key concepts from programming tutorials")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload tutorial video", type=["mp4", "mov", "avi", "mkv"], 
                                    key="video_uploader")
    
    # Clip settings
    col1, col2 = st.columns(2)
    with col1:
        num_clips = st.slider("Number of clips to generate", 1, 5, 3, key="num_clips")
    with col2:
        clip_duration = st.slider("Clip duration (seconds)", 30, 120, 60, key="duration")
    
    # Process button
    process_clicked = st.button("✨ Extract Code Concepts", key="extract_button", 
                               use_container_width=True, type="primary")
    
    # Only process if button is clicked and there's a file
    if process_clicked and uploaded_file:
        # Save the uploaded file to a temporary path
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            temp_path = tmp.name
        
        # Store values in session state
        st.session_state.temp_path = temp_path
        st.session_state.clip_duration = clip_duration
        
        # Process the video
        process_tutorial(temp_path, num_clips, clip_duration)
    
    # Display results if processing is complete
    display_results()
    
    # Footer
    st.markdown("""
    ---
    ### 🚀 How It Works
    1. Upload any programming tutorial video
    2. AI analyzes the content to find the most educational code examples
    3. Get ready-to-share clips with descriptive titles
    4. Download and post to Twitter, LinkedIn, Instagram, etc.
    
    Powered by AssemblyAI and Streamlit
    """)


if __name__ == "__main__":
    main()