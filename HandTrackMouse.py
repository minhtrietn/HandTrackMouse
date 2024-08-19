import math
import cv2
import mediapipe as mp
import win32api
import win32con


def on_pressed(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)

def on_released(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                middle_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                h, w, _ = image.shape
                thumb_tip_x, thumb_tip_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
                middle_pip_x, middle_pip_y = int(middle_pip.x * w), int(middle_pip.y * h)
                index_tip_x, index_tip_y = int(index_tip.x * w), int(index_tip.y * h)

                distance = math.hypot(thumb_tip_x - middle_pip_x, thumb_tip_y - middle_pip_y)

                cv2.circle(image, (thumb_tip_x, thumb_tip_y), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(image, (middle_pip_x, middle_pip_y), 10, (0, 0, 255), cv2.FILLED)
                cv2.circle(image, (index_tip_x, index_tip_y), 10, (0, 255, 0), cv2.FILLED)

                cv2.line(image, (thumb_tip_x, thumb_tip_y), (middle_pip_x, middle_pip_y), (0, 255, 255), 3)

                cv2.putText(image, f'{int(distance)} px',
                            ((thumb_tip_x + middle_pip_x) // 2, (thumb_tip_y + middle_pip_y) // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                if results.multi_hand_landmarks:
                    win32api.SetCursorPos((index_tip_x, index_tip_y))

                    if distance < 50:
                        on_pressed(index_tip_x, index_tip_y)
                    else:
                        on_released(index_tip_x, index_tip_y)

        cv2.imshow("Hands", image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
