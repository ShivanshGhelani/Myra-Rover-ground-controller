# Special Command Constants
STOP = 0x00
MOVE_FORWARD = 0x01
MOVE_BACKWARD = 0x02
TURN_LEFT = 0x03
TURN_RIGHT = 0x04
MOVE_FORWARD_LEFT = 0x05
MOVE_FORWARD_RIGHT = 0x06
MOVE_BACKWARD_LEFT = 0x07
MOVE_BACKWARD_RIGHT = 0x08
SPIN_CLOCKWISE = 0x09
SPIN_COUNTERCLOCKWISE = 0x0A
DIAGONAL_LEFT = 0x0B
DIAGONAL_RIGHT = 0x0C
DIAGONAL_LEFT_REVERSE = 0x0D
DIAGONAL_RIGHT_REVERSE = 0x0E
MANUAL_MODE_AUTONOMOUS_MODE = 0x0F     
VOICE_COMMAND_MODE = 0x16

esp32_ip = '192.168.4.1'  # Default IP for ESP32 SoftAP
port = 80  # Port used by the ESP32 server


commands = {
    "forward": MOVE_FORWARD,
    "backward": MOVE_BACKWARD,
    "left": TURN_LEFT,
    "right": TURN_RIGHT,
    "clockwise": SPIN_CLOCKWISE,
    "counterclockwise": SPIN_COUNTERCLOCKWISE,
    "stop": STOP,
    #Add more commands as needed
}
    

def send_single_byte_command(command_byte):
    """Send a single byte command to the ESP32."""
    import socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((esp32_ip, port)) 
        client_socket.sendall(f"0x{command_byte:02X}\n".encode('utf-8'))
        print(f"Command Sent: 0x{command_byte:02X}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def send_two_byte_command(command_byte, value):
    """Send a command with a speed to the ESP32."""
    import socket
    import time
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((esp32_ip, port)) 
        client_socket.sendall(f"0x{command_byte:02X} {value}\n".encode('utf-8'))
        time.sleep(0.005)
        print(f"Command Sent: 0x{command_byte:02X} {value}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
