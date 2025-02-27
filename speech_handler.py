import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
from config import LANGUAGE, RATE, VOLUME, VOICE_ID, WAKE_WORD

class SpeechHandler:
    def __init__(self):
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Create temp directory for audio files if it doesn't exist
        self.temp_dir = "temp"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def listen(self):
        """Listen for user input and return the recognized text"""
        with sr.Microphone() as source:
            print("\n🎤 Listening... (Speak now)")
            # Adjust for ambient noise and increase dynamic energy threshold
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 4000  # Increase if needed
            
            try:
                # Show visual feedback that we're listening
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("🔍 Processing your speech...")
                
                text = self.recognizer.recognize_google(audio, language=LANGUAGE)
                print(f"\n👥 You said: {text}")
                return text.lower()
                    
            except sr.WaitTimeoutError:
                print("⏰ Listening timed out. Please try again.")
                return None
            except sr.UnknownValueError:
                print("❌ Could not understand audio. Please speak clearly and try again.")
                return None
            except sr.RequestError as e:
                print(f"🚫 Error with the speech service; {e}")
                return None

    def speak(self, text):
        """Convert text to speech"""
        print(f"\n🤖 Assistant: {text}")
        try:
            print("🔊 Generating speech...")
            # Create gTTS object
            tts = gTTS(text=text, lang=LANGUAGE.split('-')[0])
            # Save to temporary file
            temp_file = os.path.join(self.temp_dir, "temp.mp3")
            tts.save(temp_file)
            # Play the audio
            playsound(temp_file)
            # Clean up
            try:
                os.remove(temp_file)
            except:
                pass
        except Exception as e:
            print(f"🚫 Error in speech synthesis: {e}")

    def is_wake_word(self, text):
        """Check if the wake word is in the text"""
        if text and WAKE_WORD in text.lower():
            print(f"🎯 Wake word '{WAKE_WORD}' detected!")
            return True
        return False 