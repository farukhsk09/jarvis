# Jarvis Voice Assistant

A voice-based AI assistant that can process audio questions and provide spoken responses using Ollama LLM.

## Features

- Process audio files (.m4a format) containing questions
- Transcribe speech to text
- Generate responses using Ollama LLM
- Convert responses back to speech
- Handle multiple questions per audio file
- Split long responses into multiple audio files
- Wake word detection ("jarvis")

## Prerequisites

- Python 3.10 or higher
- FFmpeg
- PortAudio
- Ollama running locally (default: http://127.0.0.1:11434)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jarvis.git
   cd jarvis
   ```

2. Create your configuration:
   ```bash
   cp config.py.template config.py
   # Edit config.py with your preferred settings
   ```

3. Set up the environment:
   ```bash
   cp setup.sh.template setup.sh
   chmod +x setup.sh
   ./setup.sh
   ```

4. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Usage

1. Place your .m4a audio files in the `resources/input` directory

2. Run the assistant:
   ```bash
   python main.py
   ```

3. Check the output:
   - Text transcripts: `resources/output/qa_session_*.txt`
   - Audio responses: `resources/output/qa_session_*.mp3`
   - Logs: `resources/output/jarvis.log`

## Directory Structure

```
jarvis/
├── src/                    # Source code
├── resources/
│   ├── input/             # Place audio files here
│   ├── output/            # Generated responses
│   └── temp/              # Temporary files
├── config.py              # Configuration (create from template)
├── requirements.txt       # Python dependencies
└── setup.sh              # Setup script (create from template)
```

## Configuration

Edit `config.py` to customize:
- Ollama model name
- Wake word
- Language settings
- Voice settings

## Limitations

- Only processes .m4a audio files
- Requires Ollama running locally
- Responses are truncated at 2000 words
- Audio chunks are limited to 1000 words each

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - See LICENSE file for details 
