import cv2
import mediapipe as mp
import numpy as np
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

neutral_pitch = 0
neutral_roll = 0
neutral_set = False
last_time = 0
cooldown = 0.6
last_action = ""



def get_vector_angle(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return np.degrees(np.arccos(np.clip(np.dot(a, b), -1.0, 1.0)))

def get_pitch_roll(landmarks):
    wrist = np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z])
    index = np.array([landmarks[5].x, landmarks[5].y, landmarks[5].z])
    pinky = np.array([landmarks[17].x, landmarks[17].y, landmarks[17].z])

    v1 = index - wrist
    v2 = pinky - wrist
    normal = np.cross(v1, v2)

    down = np.array([0, 1, 0])
    right = np.array([1, 0, 0])

    pitch = get_vector_angle(normal, down) - 90
    roll = get_vector_angle(normal, right) - 90

    # Fix sign
    if normal[0] < 0: roll *= -1
    if normal[1] > 0: pitch *= -1

    return pitch, roll

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
        landmarks = hand.landmark
        pitch, roll = get_pitch_roll(landmarks)

        if neutral_set:
            dp = pitch - neutral_pitch
            dr = roll - neutral_roll

            pitch_dead_zone = 5
            roll_dead_zone = 6
            dominance_margin = 6

            if abs(dp) < pitch_dead_zone: dp = 0
            if abs(dr) < roll_dead_zone: dr = 0

            action = None
            now = time.time()

            if now - last_time > cooldown:
                # Ensure movement is clearly dominant
                if abs(dp) > abs(dr) + dominance_margin:
                    if dp > 8:
                        action = "FORWARD"
                    elif dp < -12 and abs(dr) < 8:  # Prevent false backward if rolling
                        action = "BACKWARD"
                elif abs(dr) > abs(dp) + dominance_margin:
                    if dr < -12:
                        action = "TURN LEFT"
                    elif dr > 12:
                        action = "TURN RIGHT"

                if action and action != last_action:
                    print(">>>", action)
                    last_action = action
                    last_time = now

            cv2.putText(frame, f"ΔPitch: {dp:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(frame, f"ΔRoll:  {dr:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        else:
            cv2.putText(frame, "Press 'r' to set NEUTRAL pose", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    else:
        cv2.putText(frame, "Show one hand", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

    cv2.putText(frame, "Press 'r' to set NEUTRAL pose | 'q' to quit", (10, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    cv2.imshow("Gesture IMU Control", frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('r') and results.multi_hand_landmarks:
        landmarks = results.multi_hand_landmarks[0].landmark
        neutral_pitch, neutral_roll = get_pitch_roll(landmarks)
        neutral_set = True
        print("✅ Neutral pose set.")

cap.release()
cv2.destroyAllWindows()
