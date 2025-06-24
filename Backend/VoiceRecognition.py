import speech_recognition as sr
import pyaudio
import threading
import queue
import time
from dotenv import dotenv_values
from Backend.Utils import QueryModifier
import mtranslate as mt

env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.audio_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.is_listening = False
        self.setup_microphone()
        
    def setup_microphone(self):
        """Setup microphone with optimal settings"""
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Microphone setup complete")
        except Exception as e:
            print(f"Error setting up microphone: {e}")
    
    def listen_continuously(self, gui_update_queue):
        """Listen continuously for voice input"""
        def audio_callback(recognizer, audio):
            try:
                # Use Google Speech Recognition
                text = recognizer.recognize_google(audio, language=InputLanguage)
                
                # Translate if not English
                if not InputLanguage.lower().startswith("en"):
                    gui_update_queue.put(('status', "Translating..."))
                    text = mt.translate(text, "en", "auto")
                
                # Process and queue the result
                processed_text = QueryModifier(text)
                self.result_queue.put(processed_text)
                
            except sr.UnknownValueError:
                pass  # No speech detected
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
        
        # Start background listening
        self.stop_listening = self.recognizer.listen_in_background(
            self.microphone, audio_callback, phrase_time_limit=5
        )
        self.is_listening = True
    
    def get_speech_result(self):
        """Get speech recognition result if available"""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop_listening_continuous(self):
        """Stop continuous listening"""
        if hasattr(self, 'stop_listening') and self.is_listening:
            self.stop_listening(wait_for_stop=False)
            self.is_listening = False
    
    def listen_once(self, timeout=5):
        """Listen for a single command with timeout"""
        try:
            with self.microphone as source:
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            
            print("Processing...")
            text = self.recognizer.recognize_google(audio, language=InputLanguage)
            
            # Translate if needed
            if not InputLanguage.lower().startswith("en"):
                text = mt.translate(text, "en", "auto")
            
            return QueryModifier(text)
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None

# Global voice recognizer instance
voice_recognizer = VoiceRecognizer()

def SpeechRecognition(gui_update_queue=None):
    """Main speech recognition function"""
    if gui_update_queue:
        gui_update_queue.put(('status', "Listening..."))
    
    result = voice_recognizer.listen_once()
    
    if gui_update_queue and result:
        gui_update_queue.put(('status', "Processing..."))
    
    return result

if __name__ == "__main__":
    # Test voice recognition
    while True:
        result = SpeechRecognition()
        if result:
            print(f"Recognized: {result}")