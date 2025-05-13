import socket
import mediapipe as mp
import cv2
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

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

import time
gesture_stability_time = 0.5  # seconds
last_command_time = time.time()


esp32_ip = '192.168.4.1'  # Default IP for ESP32 SoftAP
port = 80  # Port used by the ESP32 server

def send_single_byte_command(command_byte):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((esp32_ip, port)) 
        client_socket.sendall(f"0x{command_byte:02X}\n".encode('utf-8'))
        print(f"Command Sent: 0x{command_byte:02X}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

    # print(f"Command Sent: 0x{command_byte:02X}")


while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            # === Hand Landmark Data ===

            lm = handLms.landmark
            current_command = None
            text = "No gesture"
            hand_type = result.multi_handedness[0].classification[0].label  # "Left" or "Right"
            thumb_up = lm[4].x < lm[3].x if hand_type == "Right" else lm[4].x > lm[3].x

            if not hasattr(send_single_byte_command, 'previous_command'):
                send_single_byte_command.previous_command = None

            # === Helper: Check if finger is up ===
            def finger_is_up(tip, pip):
                return lm[tip].y < lm[pip].y

            # === Finger Status ===
            fingers = {
                "thumb": thumb_up,  # Thumb: left of base (for right hand)
                "index": finger_is_up(8, 6),
                "middle": finger_is_up(12, 10),
                "ring": finger_is_up(16, 14),
                "pinky": finger_is_up(20, 18),
            }

            # === Gesture Recognition Logic ===

            # Fist
            if not any(fingers.values()):
                current_command = STOP
                text = "Stop"
            
            # Open Palm (All up)
            elif all(fingers.values()):
                current_command = STOP
                text = "Idle"

            # Thumbs Up (only thumb)
            elif fingers["thumb"] and not (fingers["index"] or fingers["middle"] or fingers["ring"] or fingers["pinky"]):
                current_command = MOVE_FORWARD
                text = "Forward"

            # Rock Sign (index + pinky + thumb)
            elif fingers["index"] and fingers["pinky"] and fingers['thumb'] and not fingers["middle"] and not fingers["ring"] :
                current_command = MOVE_BACKWARD
                text = "Backward"

            # Peace (index + middle)
            elif fingers["index"] and fingers["middle"] and not fingers["ring"] and not fingers["pinky"] and not fingers["thumb"]:
                current_command = TURN_LEFT
                text = "Turn Left"

            # Index Only
            elif fingers["index"] and not fingers["middle"] and not fingers["pinky"] and not fingers["ring"] and not fingers["thumb"]:
                current_command = TURN_RIGHT
                text = "Turn Right"

            # Gun Sign (thumb + index)
            elif fingers["thumb"] and fingers["index"] and not fingers["middle"] and not fingers["ring"] and not fingers["pinky"]:
                
                current_command = SPIN_CLOCKWISE
                text = "Spin CCW"

            # Call Me Sign (thumb + pinky)
            elif fingers["thumb"] and fingers["pinky"] and not fingers["index"] and not fingers["middle"] and not fingers["ring"]:
                current_command = SPIN_COUNTERCLOCKWISE
                text = "Spin CW"

            # === Show Text on Screen ===
            cv2.putText(frame, text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

            now = time.time()
            if current_command != send_single_byte_command.previous_command and current_command is not None:
                if now - last_command_time > gesture_stability_time:
                    send_single_byte_command(current_command)
                    send_single_byte_command.previous_command = current_command
                    last_command_time = now


            # print("Fingers:", fingers)

    cv2.imshow("Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
