import speech_recognition as sr
import threading
from constants import *

class VoiceController:
    def __init__(self):
        self.voice_command_mode = False
        self.voice_thread = None
        self.recognizer = sr.Recognizer()

    def toggle_voice_command_mode(self):
        """Toggle between voice command and gamepad modes."""
        self.voice_command_mode = not self.voice_command_mode

        if self.voice_command_mode:
            print("Switched to Voice Command Mode")
            self.voice_thread = threading.Thread(target=self.start_listening_for_commands, daemon=True)
            self.voice_thread.start()
        else:
            print("Switched to Gamepad Mode")

    def start_listening_for_commands(self):
        """Start listening for voice commands."""
        microphone = sr.Microphone(device_index=1)
        with microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)

            while self.voice_command_mode:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio)
                    print(f"Recognized: {text}")
                    self.process_command(text)

                except sr.UnknownValueError:
                    pass  # Ignore unrecognized speech
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                except sr.WaitTimeoutError:
                    pass  # Ignore timeout errors and continue listening

    def process_command(self, text):
        """Process the recognized voice command."""
        text = text.lower().strip()

        if text == "exit":
            self.voice_command_mode = False
            print("Switched back to Gamepad Mode")
            return

        # First try exact command match
        if text in commands:
            send_single_byte_command(commands[text])
            return

        # Then try to find any command word in the phrase
        for command_word, command_byte in commands.items():
            if command_word in text:
                send_single_byte_command(command_byte)
                return

        print(f"Command not recognized: {text}")
        print(f"Available commands: {', '.join(commands.keys())}")
