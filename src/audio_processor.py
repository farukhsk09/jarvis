import speech_recognition as sr
from gtts import gTTS
import os
from pathlib import Path
import logging
from pydub import AudioSegment
import tempfile

class AudioProcessor:
    def __init__(self, input_dir, output_dir, temp_dir):
        self.recognizer = sr.Recognizer()
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self._setup_directories()
        self._setup_logging()

    def _setup_directories(self):
        """Ensure all required directories exist"""
        for dir_path in [self.input_dir, self.output_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.output_dir / 'audio_processing.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _convert_m4a_to_wav(self, m4a_path):
        """Convert M4A file to WAV format"""
        try:
            self.logger.info(f"Converting {m4a_path.name} to WAV format...")
            audio = AudioSegment.from_file(str(m4a_path), format="m4a")
            
            # Create a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', dir=self.temp_dir, delete=False) as temp_wav:
                wav_path = temp_wav.name
                audio.export(wav_path, format="wav")
                self.logger.info(f"Successfully converted to WAV: {wav_path}")
                return wav_path
        except Exception as e:
            self.logger.error(f"Error converting M4A to WAV: {e}")
            return None

    def transcribe_audio(self, audio_file):
        """Transcribe audio file to text"""
        input_path = self.input_dir / audio_file
        self.logger.info(f"Starting transcription of: {audio_file}")
        
        if not input_path.exists():
            self.logger.error(f"Audio file not found: {input_path}")
            return None

        try:
            # Convert M4A to WAV if necessary
            if input_path.suffix.lower() == '.m4a':
                wav_path = self._convert_m4a_to_wav(input_path)
                if not wav_path:
                    return None
            else:
                wav_path = str(input_path)

            with sr.AudioFile(wav_path) as source:
                self.logger.info("Recording audio from file...")
                audio = self.recognizer.record(source)
                
                self.logger.info("Performing speech recognition...")
                text = self.recognizer.recognize_google(audio)
                self.logger.info(f"Successfully transcribed text: {text}")
                
                # Clean up temporary WAV file if it was created
                if input_path.suffix.lower() == '.m4a':
                    os.unlink(wav_path)
                    self.logger.info("Cleaned up temporary WAV file")
                
                return text

        except sr.UnknownValueError:
            self.logger.error("Speech recognition could not understand the audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Could not request results from speech recognition service: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during transcription: {e}")
            return None

    def text_to_speech(self, text, output_file):
        """Convert text to speech and save as audio file"""
        try:
            self.logger.info(f"Converting text to speech: {text[:100]}...")
            tts = gTTS(text=text, lang='en')
            output_path = self.output_dir / output_file
            tts.save(str(output_path))
            self.logger.info(f"Successfully saved audio to: {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error generating speech: {e}")
            return False 