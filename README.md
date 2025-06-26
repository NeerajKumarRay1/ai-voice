# Voice-Based AI Assistant

A Python-based voice assistant that uses OpenAI's Whisper for speech-to-text, GPT-4o for understanding and generating responses, and ElevenLabs (or pyttsx3 as fallback) for text-to-speech. The assistant also includes a knowledge base using FAISS for vector search and a web interface using either Flask or Gradio.

## Project Structure

- `main.py`: Main voice interaction loop
- `stt.py`: Handles speech-to-text using Whisper
- `tts.py`: Handles text-to-speech using ElevenLabs or pyttsx3
- `chat.py`: Handles LLM prompts and LangChain integration
- `knowledge_base.py`: Loads FAQ into FAISS vector database
- `utils.py`: Helper functions
- `app.py`: Web interface using Flask or Gradio
- `requirements.txt`: List of required packages
- `config.json`: Configuration file (created on first run)

## Setup

1. Clone this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Set up your API keys:
   - Create a `config.json` file or let the application create one on first run
   - Add your OpenAI API key and ElevenLabs API key

## Configuration

The application uses a `config.json` file for configuration. If not present, a default one will be created on first run. Key configuration options include:

- API keys for OpenAI and ElevenLabs
- Model settings for Whisper and GPT-4o
- Voice settings for text-to-speech
- Knowledge base settings
- Web interface settings

## Usage

### Voice Assistant Mode

Run the main voice interaction loop:

```bash
python main.py
```

### Web Interface

Start the web interface (Flask or Gradio, as configured):

```bash
python app.py
```

## Adding Knowledge

Place your knowledge documents in the `knowledge` directory (created on first run). Supported formats include:

- Text files (.txt)
- Markdown files (.md)
- JSON files (.json)

The knowledge base will be automatically built on first run.

## Dependencies

- Whisper (OpenAI) for speech-to-text
- GPT-4o (OpenAI) for understanding and replying
- ElevenLabs or pyttsx3 for text-to-speech
- LangChain for prompt management and retrieval
- FAISS as the vector database
- Flask or Gradio for the web interface
- Pygame for audio playback

## Text-to-Speech Module

The TTS module (`tts.py`) provides text-to-speech functionality using ElevenLabs API with a fallback to pyttsx3.

### TTS Features

- Uses ElevenLabs API for high-quality speech synthesis when an API key is available
- Falls back to pyttsx3 for offline text-to-speech when ElevenLabs is not available
- Provides both standalone functions and a class-based interface
- Handles temporary file management and cleanup
- Cross-platform audio playback using pygame

### TTS Usage

#### Standalone Function

```python
from tts import speak_text

# Simple usage
speak_text("Hello, this is a test.")

# Check if ElevenLabs is available
from tts import is_elevenlabs_available
if is_elevenlabs_available():
    print("Using ElevenLabs for high-quality speech")
else:
    print("Using pyttsx3 fallback")
```

#### Class-based Interface

```python
from tts import TextToSpeech

# Configuration
config = {
    'use_elevenlabs': True,
    'elevenlabs_api_key': 'your_api_key_here',  # Or use environment variable
    'elevenlabs_voice_id': '21m00Tcm4TlvDq8ikWAM',  # Default voice ID
    'tts_cache_dir': 'tts_cache'
}

# Initialize
tts = TextToSpeech(config)

# Speak text
tts.speak("Hello, this is a test using the TextToSpeech class.")

# Clean up resources when done
tts.cleanup()
```

### Testing TTS

Use the included test script to verify functionality:

```bash
# Test standalone functions
python test_tts.py --mode standalone

# Test class-based interface
python test_tts.py --mode class

# Test both
python test_tts.py --mode both

# Set API key for testing
python test_tts.py --set-api-key YOUR_API_KEY
```

## License

This project is open source and available under the MIT License.