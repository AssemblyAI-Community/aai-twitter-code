#!/usr/bin/env python3
"""
VerbalizeCode: Transform verbal code descriptions into actual code
Record yourself describing code functionality and get working code back
using AssemblyAI's transcription and LeMUR capabilities.
"""

import os
import argparse
import tempfile
import wave
import pyaudio
import assemblyai as aai
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from dotenv import load_dotenv

console = Console()
load_dotenv()

# Initialize AssemblyAI
aai_key = os.getenv("ASSEMBLYAI_API_KEY")
if not aai_key:
    console.print("[bold red]Error:[/] ASSEMBLYAI_API_KEY not found in environment variables.")
    exit(1)
aai.settings.api_key = aai_key

def record_audio(duration=20, sample_rate=44100):
    """Record audio from microphone for specified duration"""
    console.print(f"[bold green]Recording[/] your code description for {duration} seconds...")
    
    chunk = 1024
    audio_format = pyaudio.paInt16
    channels = 1
    
    audio = pyaudio.PyAudio()
    stream = audio.open(format=audio_format, channels=channels, rate=sample_rate,
                       input=True, frames_per_buffer=chunk)
    
    frames = []
    for i in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
        if i % 10 == 0:
            seconds_left = duration - int((i * chunk) / sample_rate)
            console.print(f"⏱️ {seconds_left} seconds remaining...", end="\r")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        wf = wave.open(tmp_file.name, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(audio_format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        return tmp_file.name

def generate_code(audio_file, language):
    """Transcribe audio and generate code using LeMUR"""
    with console.status("[bold blue]Transcribing your description...") as status:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file)
        
        # Store transcript text for later display
        transcribed_text = transcript.text
        
        status.update("[bold blue]Generating code from your description...")
        
        code_prompt = f"""
        Transform this verbal description into working {language} code:
        
        {transcribed_text}
        
        IMPORTANT: RETURN ONLY THE CODE. DO NOT INCLUDE A PREAMBLE OR ANY SORT OF EXPLANATION OR INTRODUCTION. RETURN JUST CODE.
        
        Make sure it's properly formatted, efficient, and follows best practices for {language}.
        """
        
        lemur_response = transcript.lemur.task(
            code_prompt.strip(),
            final_model=aai.LemurModel.claude3_haiku
        )
        return lemur_response.response, transcribed_text

def main():
    parser = argparse.ArgumentParser(description="Transform verbal code descriptions into actual code")
    parser.add_argument("--language", "-l", default="python", 
                        help="Programming language (default: python)")
    parser.add_argument("--duration", "-d", type=int, default=20, 
                        help="Recording duration in seconds (default: 20)")
    parser.add_argument("--output", "-o", help="Output file (optional)")
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "[bold cyan]💻 VerbalizeCode: Speech-to-Code Generator 🎤[/]\n"
        f"Describe the code you want in [bold yellow]{args.language}[/] and I'll create it!",
        title="🧙 Speech-to-Code", subtitle="Powered by AssemblyAI"
    ))
    
    try:
        audio_file = record_audio(duration=args.duration)
        console.print("[green]✓[/] Recording complete!")
        
        code, transcribed_text = generate_code(audio_file, args.language)
        
        # Clean up the code (remove markdown code blocks if present)
        clean_code = code.replace("```" + args.language, "").replace("```", "").strip()
        
        # Display the transcribed text
        console.print(Panel(
            transcribed_text, 
            title="📝 Your Transcribed Description", 
            border_style="blue", 
            expand=False
        ))
        
        console.print("\n[bold cyan]↓ Transformed Into Code ↓[/]\n")
        
        # Display the code with syntax highlighting
        console.print(Panel(
            Syntax(clean_code, args.language, theme="monokai", line_numbers=True),
            title=f"💻 {args.language.capitalize()} Code Generated", border_style="green"
        ))
        
        # Save to file if requested
        if args.output:
            with open(args.output, "w") as f:
                f.write(clean_code)
            console.print(f"[bold green]Code saved to:[/] {args.output}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
    finally:
        if 'audio_file' in locals() and os.path.exists(audio_file):
            os.remove(audio_file)

if __name__ == "__main__":
    main()