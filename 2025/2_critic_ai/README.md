# 🎬 CriticAI: Voice-to-Professional Movie Review Generator

A Python CLI tool that transforms your casual spoken movie thoughts into professional-sounding critic reviews using AssemblyAI.

![CriticAI Demo](app.png)

Follow [AssemblyAI's Twitter account](https://x.com/AssemblyAI) for more cool projects like this

## 🚀 What it does

Ever watched a movie and wanted to sound like Roger Ebert when sharing your thoughts? CriticAI:

- Records your voice as you speak about any movie
- Transcribes your casual thoughts using AssemblyAI
- Transforms your rambling into eloquent, professional-sounding movie criticism
- Formats everything into a shareable markdown review

## ⚙️ Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Rename `.env.example` as `.env` and add your [AssemblyAI API key](https://www.assemblyai.com/dashboard/signup):
   ```
   ASSEMBLYAI_API_KEY=your_api_key_here
   ```

3. **Note on PyAudio Installation:**
   
   PyAudio may require additional system dependencies before installing with pip:
   
   - **On Ubuntu/Debian:**
     ```bash
     sudo apt-get install portaudio19-dev python3-pyaudio
     ```
   
   - **On macOS (using Homebrew):**
     ```bash
     brew install portaudio
     ```
   
   - **On Windows:**
     You may need to install a pre-compiled wheel if pip installation fails:
     ```bash
     pip install pipwin
     pipwin install pyaudio
     ```

## 🎯 Usage

Run the script with the movie title:

```bash
python main.py --title "The Matrix" --duration 20
```

This will:

1. Record your voice for 20 seconds as you talk about The Matrix
2. Transcribe your audio
3. Transform your casual thoughts into a professional review
4. Save the review as `the_matrix_review.md`


## 🎭 Example

**What you say:**
> "So I just watched The Matrix again and it really holds up. The effects are still cool and Neo is such a great character. The fighting scenes are awesome. I kinda forgot how philosophical it gets too. Definitely one of my favorites."

**What CriticAI generates:**
> # The Matrix: A Landmark of Cinematic Philosophy
> 
> The Wachowskis' groundbreaking 1999 sci-fi masterpiece "The Matrix" remains, even decades after its release, a towering achievement in both visual innovation and philosophical storytelling. The film's revolutionary "bullet time" special effects—which sent shockwaves through Hollywood upon release—maintain their visceral impact, demonstrating how truly paradigm-shifting technical innovations can transcend their era.
> 
> Keanu Reeves delivers perhaps his most iconic performance as Neo, embodying both vulnerability and latent heroism with a nuanced restraint that belies the film's action-heavy exterior. His transformation from disaffected hacker to messianic figure provides the emotional backbone for what could have otherwise been merely an exercise in style over substance.
> 
> What elevates "The Matrix" beyond mere science fiction spectacle is its ambitious philosophical underpinnings. Drawing from sources as diverse as Plato's allegory of the cave, Baudrillard's simulacra theory, and Eastern mysticism, the Wachowskis crafted a narrative that invites—even demands—intellectual engagement alongside its expertly choreographed combat sequences. The film's central red pill/blue pill dichotomy has transcended cinema to become cultural shorthand for choosing between comfortable illusion and harsh reality.
> 
> The balletic violence, choreographed by the legendary Yuen Woo-ping, redefined action filmmaking for a generation. These sequences aren't merely technical showcases but character-defining moments that advance both narrative and theme with remarkable economy.
> 
> "The Matrix" stands as that rarest of Hollywood creations: a blockbuster of ideas, a commercial juggernaut that refuses to underestimate its audience. Its influence on cinema, fashion, and cultural discourse cannot be overstated, and its central questions about reality, free will, and consciousness remain as pertinent today as in 1999.
> 
> ★★★★★