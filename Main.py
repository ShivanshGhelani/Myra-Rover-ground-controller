import time
from constants import send_single_byte_command, STOP
from voice_controller import VoiceController
from gamepad_controller import GamepadController

def main():
    try:
        # Initialize controllers
        voice_controller = VoiceController()
        gamepad_controller = GamepadController()
        
        # Set up controller references
        gamepad_controller.set_voice_controller(voice_controller)

        while True:
            gamepad_controller.process_events()
            time.sleep(0.05)  # Small delay to avoid CPU overload

    except KeyboardInterrupt:
        send_single_byte_command(STOP)

if __name__ == "__main__":
    main()