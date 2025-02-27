#!/bin/bash

# Ensure we're in the jarvis directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Create required directories
mkdir -p resources/input resources/output resources/temp

# Detect OS and install required system dependencies
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Installing system dependencies for macOS..."
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install required packages
    brew install python@3.10 portaudio flac ffmpeg
    
    # Link Python 3.10
    brew link python@3.10
    
    # Install PyAudio using Homebrew
    brew install pyaudio
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Installing system dependencies for Linux..."
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y python3-dev portaudio19-dev python3-pyaudio ffmpeg
    elif command -v dnf &> /dev/null; then
        # Fedora
        sudo dnf install -y portaudio-devel python3-pyaudio ffmpeg
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -S portaudio python-pyaudio ffmpeg
    fi
fi

# Create an alias for python to python3
if [[ -f ~/.bashrc ]]; then
    echo "alias python=python3" >> ~/.bashrc
    source ~/.bashrc
elif [[ -f ~/.zshrc ]]; then
    echo "alias python=python3" >> ~/.zshrc
    source ~/.zshrc
fi

# Remove existing venv if it exists
rm -rf venv

# Create new virtual environment with Python 3.10
python3.10 -m venv venv
source venv/bin/activate

# Verify python version and venv activation
python --version
which python

# Upgrade pip and install basic tools
python -m pip install --upgrade pip setuptools wheel

# For macOS, install pyobjc packages first
if [[ "$OSTYPE" == "darwin"* ]]; then
    python -m pip install --no-cache-dir \
        pyobjc-core \
        pyobjc-framework-Cocoa \
        pyobjc-framework-Quartz \
        pyobjc-framework-CoreText \
        pyobjc-framework-ApplicationServices
fi

# Install requirements
pip install -r requirements.txt

# Verify installations
python -c "import speech_recognition; import gtts; import requests; import pyaudio; import playsound; import pydub; print('All modules installed successfully!')"

echo "Setup complete! To start the assistant, run:"
echo "source venv/bin/activate"
echo "python main.py"

# Create a README with instructions
cat > README.md << EOL
# Jarvis Voice Assistant

## Setup Instructions

1. Run the setup script:
   \`\`\`bash
   ./setup.sh
   \`\`\`

2. Place your .m4a audio files in the \`resources/input\` directory

3. Activate the virtual environment:
   \`\`\`bash
   source venv/bin/activate
   \`\`\`

4. Run the assistant:
   \`\`\`bash
   python main.py
   \`\`\`

## Directory Structure

- \`resources/input\`: Place your .m4a audio files here
- \`resources/output\`: Contains transcribed text and generated audio responses
- \`resources/temp\`: Temporary files used during processing
- \`src/\`: Source code files

## Logging

Logs are available in:
- \`resources/output/jarvis.log\`: Main application log
- \`resources/output/audio_processing.log\`: Audio processing specific log

## Requirements

- Python 3.10 or higher
- FFmpeg (installed automatically by setup script)
- Internet connection for speech recognition
EOL 