"""
A simple custom controller to demonstrate sending commands to the Myra Rover.
This file shows different ways to control the rover using the command constants.
"""

import time
import keyboard  # for keyboard control
from constants import *

class CustomController:
    def __init__(self):
        self.running = True
        self.current_speed = 128  # middle speed value (0-255)
        
    def increase_speed(self):
        self.current_speed = min(255, self.current_speed + 25)
        print(f"Speed increased to: {self.current_speed}")
        
    def decrease_speed(self):
        self.current_speed = max(0, self.current_speed - 25)
        print(f"Speed decreased to: {self.current_speed}")

    def keyboard_control(self):
        """
        Simple keyboard control:
        Arrow keys for movement
        Space for stop
        Q/E for rotation
        +/- for speed control
        ESC to quit
        """
        print("\nKeyboard Control Active:")
        print("↑/↓/←/→ : Movement")
        print("Space   : Stop")
        print("Q/E     : Rotate Left/Right")
        print("+/-     : Speed Up/Down")
        print("ESC     : Quit\n")

        while self.running:
            if keyboard.is_pressed('up'):
                send_two_byte_command(MOVE_FORWARD, self.current_speed)
            elif keyboard.is_pressed('down'):
                send_two_byte_command(MOVE_BACKWARD, self.current_speed)
            elif keyboard.is_pressed('left'):
                send_single_byte_command(TURN_LEFT)
            elif keyboard.is_pressed('right'):
                send_single_byte_command(TURN_RIGHT)
            elif keyboard.is_pressed('q'):
                send_single_byte_command(SPIN_COUNTERCLOCKWISE)
            elif keyboard.is_pressed('e'):
                send_single_byte_command(SPIN_CLOCKWISE)
            elif keyboard.is_pressed('space'):
                send_single_byte_command(STOP)
            elif keyboard.is_pressed('+'):
                self.increase_speed()
                time.sleep(0.2)  # Debounce
            elif keyboard.is_pressed('-'):
                self.decrease_speed()
                time.sleep(0.2)  # Debounce
            elif keyboard.is_pressed('esc'):
                self.running = False
                send_single_byte_command(STOP)
                print("Controller stopped")
                break
            
            time.sleep(0.05)  # Control loop rate

    def sequence_demo(self):
        """
        Demonstrates a pre-programmed sequence of movements
        """
        print("Running movement sequence demo...")
        
        # Define a sequence of movements with duration
        sequence = [
            (MOVE_FORWARD, 2),
            (TURN_LEFT, 1),
            (MOVE_FORWARD, 2),
            (TURN_RIGHT, 1),
            (MOVE_BACKWARD, 2),
            (SPIN_CLOCKWISE, 1),
            (STOP, 0)
        ]

        for command, duration in sequence:
            print(f"Executing command: {hex(command)}")
            send_single_byte_command(command)
            time.sleep(duration)

def main():
    controller = CustomController()
    
    print("\nMyra Rover Custom Controller")
    print("1. Keyboard Control")
    print("2. Sequence Demo")
    print("3. Exit")
    
    while True:
        choice = input("\nSelect control mode (1-3): ")
        
        if choice == '1':
            controller.keyboard_control()
        elif choice == '2':
            controller.sequence_demo()
        elif choice == '3':
            print("Exiting controller...")
            send_single_byte_command(STOP)
            break
        else:
            print("Invalid choice. Please select 1-3.")

if __name__ == "__main__":
    main()
