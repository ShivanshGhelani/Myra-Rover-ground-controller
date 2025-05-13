from inputs import get_gamepad
import time
from constants import *

class GamepadController:
    def __init__(self):
        self.hat_x = 0
        self.hat_y = 0
        self.previous_btn_start_state = 0
        self.get_speed_from_trigger_value = lambda value: value
        self.voice_controller = None  # Will be set from main.py

    def set_voice_controller(self, voice_controller):
        """Set the voice controller reference."""
        self.voice_controller = voice_controller

    def get_latest_event(self):
        """Fetch the latest gamepad event."""
        events = get_gamepad()
        return events[-1] if events else None

    def handle_key_event(self, event):
        """Handle button press events."""
        key_commands = {
            "BTN_TL": SPIN_COUNTERCLOCKWISE,
            "BTN_TR": SPIN_CLOCKWISE,
            "BTN_NORTH": DIAGONAL_LEFT,
            "BTN_SOUTH": DIAGONAL_RIGHT,
            "BTN_WEST": DIAGONAL_LEFT_REVERSE,
            "BTN_EAST": DIAGONAL_RIGHT_REVERSE,
            "BTN_SELECT": MANUAL_MODE_AUTONOMOUS_MODE,
        }

        if event.code == "BTN_START":
            if event.state == 1 and self.previous_btn_start_state == 0:
                if self.voice_controller:
                    self.voice_controller.toggle_voice_command_mode()
            self.previous_btn_start_state = event.state

        elif event.code in key_commands:
            if event.state == 1:
                send_single_byte_command(key_commands[event.code])
            else:
                send_single_byte_command(STOP)

    def handle_absolute_event(self, event):
        """Handle analog inputs."""
        if event.code == "ABS_BRAKE":
            self.handle_trigger_event(event, MOVE_BACKWARD)
        elif event.code == "ABS_GAS":
            self.handle_trigger_event(event, MOVE_FORWARD)
        elif event.code.startswith('ABS_HAT0'):
            self.handle_hat_event(event)

    def handle_trigger_event(self, event, command):
        """Handle trigger inputs."""
        trigger_value = event.state
        if trigger_value > 0:
            send_two_byte_command(command, self.get_speed_from_trigger_value(trigger_value))
            self.monitor_trigger_event(event.code, command)
        else:
            send_single_byte_command(STOP)

    def monitor_trigger_event(self, trigger_code, command):
        """Monitor continuous trigger input."""
        while True:
            latest_event = self.get_latest_event()
            if not latest_event or latest_event.code != trigger_code or latest_event.state == 0:
                break
            trigger_value = latest_event.state
            send_two_byte_command(command, self.get_speed_from_trigger_value(trigger_value))

    def handle_hat_event(self, event):
        """Handle D-pad inputs."""
        if event.code == 'ABS_HAT0X':
            self.hat_x = event.state
        elif event.code == 'ABS_HAT0Y':
            self.hat_y = event.state
        
        hat_commands = {
            (0, 1): MOVE_BACKWARD,
            (0, -1): MOVE_FORWARD,
            (-1, 0): TURN_LEFT,
            (1, 0): TURN_RIGHT,
            (1, 1): MOVE_BACKWARD_RIGHT,
            (-1, 1): MOVE_BACKWARD_LEFT,
            (1, -1): MOVE_FORWARD_RIGHT,
            (-1, -1): MOVE_FORWARD_LEFT
        }

        command = hat_commands.get((self.hat_x, self.hat_y), STOP)
        send_single_byte_command(command)

    def process_events(self):
        """Process all gamepad events."""
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Key":
                self.handle_key_event(event)
            elif event.ev_type == "Absolute":
                self.handle_absolute_event(event)
