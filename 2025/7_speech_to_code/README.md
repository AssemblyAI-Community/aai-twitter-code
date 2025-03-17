# 💻 VerbalizeCode: Speech-to-Code Generator

A small Python CLI tool that transforms your verbal code descriptions into actual working code using AssemblyAI!

![Speech-to-Code Demo](app.png)

Follow [AssemblyAI's Twitter account](https://x.com/AssemblyAI) for more cool projects like this

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

Run the script with your preferred programming language:

```bash
python main.py --language python --duration 30 --output my_function.py
```

This will:

1. Record your voice for 30 seconds as you describe the code you want
2. Transcribe your audio
3. Transform your description into working code
4. Display the code with syntax highlighting
5. Save the code to the specified output file (optional)

## 🖥️ Example

**What you say:**
> "Create a function that takes a list of numbers, filters out all the even numbers, squares the remaining odd numbers, and returns the sum of those squared values. Make sure to handle empty lists by returning zero."

**What VerbalizeCode generates:**

```python
def sum_of_squared_odd_numbers(numbers):
    odd_numbers = [num ** 2 for num in numbers if num % 2 != 0]
    return sum(odd_numbers) if odd_numbers else 0
```

## 🔮 Supported Languages

VerbalizeCode works with many programming languages including:
- Python
- JavaScript
- Java
- C#
- Ruby
- Go
- PHP
- And more!

## 💡 Tips for Best Results

- Speak clearly and describe the code's purpose and functionality
- Mention edge cases you want the code to handle
- Specify any particular algorithms or approaches you prefer
- Describe the input and expected output for clarity