#!/usr/bin/env python3
"""
CriticAI: Voice-to-Professional Movie Review Generator
Record your casual thoughts about a movie and transform them into a professional review
using AssemblyAI's transcription and LeMUR capabilities.
"""

import os
import argparse
import tempfile
import pyaudio
import wave
import assemblyai as aai
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv
import time
from rich.progress import Progress

console = Console()

load_dotenv()

aai_key = os.getenv("ASSEMBLYAI_API_KEY")
if not aai_key:
    console.print("[bold red]Error:[/] ASSEMBLYAI_API_KEY not found in environment variables.")
    console.print("Create a .env file with your API key: ASSEMBLYAI_API_KEY=your_key_here")
    exit(1)
aai.settings.api_key = aai_key

def record_audio(duration=30, sample_rate=44100):
    """Record audio from microphone for specified duration"""
    console.print(f"[bold green]Recording[/] your movie review for {duration} seconds...")
    console.print("🎬 Start speaking now! 🎤")
    
    # Recording parameters
    chunk = 1024
    audio_format = pyaudio.paInt16
    channels = 1
    
    audio = pyaudio.PyAudio()
    
    # Open stream
    stream = audio.open(format=audio_format,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk)
    
    frames = []
    
    # Record with simpler progress indication
    start_time = time.time()
    for i in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
        elapsed = time.time() - start_time
        if i % (sample_rate // chunk) == 0:  
            percent = min(100, int((elapsed / duration) * 100))
            remaining = max(0, duration - elapsed)
            console.print(f"Recording... [magenta]{percent}%[/] {int(remaining//60):02d}:{int(remaining%60):02d}", end="\r")
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Create temp file for audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        wf = wave.open(tmp_file.name, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(audio_format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        return tmp_file.name

def generate_review(audio_file, movie_title):
    """Transcribe audio and generate a professional review using LeMUR"""
    with console.status("[bold blue]Transcribing your review...") as status:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file)
        
        status.update("[bold blue]Generating professional review...")
        
        review_prompt = f"""
        Transform this casual spoken movie review about "{movie_title}" into a 
        professional movie critic review (300-400 words).
        
        The review should:
        - Begin with an engaging hook and mention the movie title and director
        - Include a professional critic's assessment of the movie's strengths and weaknesses
        - Maintain the same overall opinion expressed in the original review
        - End with a rating out of 5 stars
        - Use sophisticated film criticism language and references
        
        Format with proper paragraphs and a star rating at the end.
        """
        
        lemur_response = transcript.lemur.task(
            review_prompt.strip(),
            final_model=aai.LemurModel.claude3_opus
        )
        return lemur_response.response

def main():
    parser = argparse.ArgumentParser(description="Transform your casual movie review into a professional critic review")
    parser.add_argument("--title", "-t", required=True, help="Title of the movie you're reviewing")
    parser.add_argument("--duration", "-d", type=int, default=30, help="Recording duration in seconds (default: 30)")
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "[bold cyan]🎬 CriticAI: Voice-to-Professional Movie Review 🎭[/]\n"
        f"Recording your thoughts about [bold yellow]{args.title}[/]",
        title="Welcome", subtitle="Powered by AssemblyAI"
    ))
    
    try:
        # Record audio
        audio_file = record_audio(duration=args.duration)
        console.print("[green]✓[/] Recording complete!")
        
        # Generate review
        console.print("\n[bold]Transforming your casual thoughts into professional criticism...[/]")
        review = generate_review(audio_file, args.title)
        
        # Print results
        console.print(Panel(Markdown(review), title=f"Professional Review: {args.title}", 
                           border_style="green", expand=False))
        
        # Save review to file
        safe_title = args.title.replace(" ", "_").lower()
        with open(f"{safe_title}_review.md", "w") as f:
            f.write(review)
        console.print(f"[bold green]Review saved to:[/] {safe_title}_review.md")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
    finally:
        if 'audio_file' in locals() and os.path.exists(audio_file):
            os.remove(audio_file)

if __name__ == "__main__":
    main()