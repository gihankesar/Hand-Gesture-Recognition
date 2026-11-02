import cv2
import mediapipe as mp
import time
import os
import numpy as np


# -------------------- MODEL SETUP --------------------

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "hand_landmarker.task"
)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.VIDEO,
    num_hands=2,
)


# -------------------- ANGLE FUNCTION --------------------

def calculate_angle(A, B, C):
    A = np.array(A)
    B = np.array(B)
    C = np.array(C)

    vector1 = A - B
    vector2 = C - B

    length1 = np.linalg.norm(vector1)
    length2 = np.linalg.norm(vector2)

    if length1 == 0 or length2 == 0:
        return None

    dot_product = np.dot(vector1, vector2)

    cosine_value = dot_product / (length1 * length2)
    angle_rad = np.arccos(
        np.clip(cosine_value, -1.0, 1.0)
    )

    return np.degrees(angle_rad)


# -------------------- TRIAL SETTINGS --------------------

COUNTDOWN_SECONDS = 3
TIMEOUT_SECONDS = 2

trial_active = False
countdown_start = None
trial_start = None
trial_done = False

print_measurements_next_frame = False


# -------------------- WEBCAM --------------------

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    raise RuntimeError("Could not open webcam.")

connections = (
    mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS
)

try:
    with HandLandmarker.create_from_options(options) as detector:

        while True:
            success, frame = camera.read()

            if not success:
                print("Couldn't read a frame!")
                break

            height, width, _ = frame.shape

            # OpenCV uses BGR; MediaPipe expects RGB.
            rgb_frame = cv2.cvtColor(
                frame, cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            timestamp_ms = int(time.perf_counter() * 1000)

            result = detector.detect_for_video(
                mp_image, timestamp_ms
            )

            # Store measurements for optional terminal output.
            measurement_data = []

            # -------------------- TRIAL TIMER --------------------

            if trial_active and not trial_done:
                countdown_elapsed = (
                    time.perf_counter() - countdown_start
                )

                if countdown_elapsed < COUNTDOWN_SECONDS:
                    remaining = (
                        COUNTDOWN_SECONDS - countdown_elapsed
                    )

                    cv2.putText(
                        frame,
                        f"Get ready: {int(remaining) + 1}",
                        (200, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        (0, 255, 255),
                        3
                    )

                else:
                    if trial_start is None:
                        trial_start = time.perf_counter()
                        print("GO! Change your hand pose!")

                    elapsed = time.perf_counter() - trial_start

                    if len(result.hand_landmarks) > 0:
                        print(
                            f"Hand detected: {elapsed:.3f} seconds"
                        )
                        trial_done = True

                    elif elapsed >= TIMEOUT_SECONDS:
                        print(
                            "Detection failed: timeout after "
                            f"{TIMEOUT_SECONDS} seconds"
                        )
                        trial_done = True

            # -------------------- PROCESS HANDS --------------------

            if len(result.hand_landmarks) == 0:
                cv2.putText(
                    frame,
                    "Gesture: No hand",
                    (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

            for hand_index, hand in enumerate(
                result.hand_landmarks
            ):
                points = []
                points_3d = []

                for landmark in hand:
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)

                    points.append((x, y))

                    points_3d.append((
                        landmark.x * width,
                        landmark.y * height,
                        landmark.z * width
                    ))

                    cv2.circle(
                        frame, (x, y), 5, (0, 255, 0), -1
                    )

                # Four finger joint angles (2D).
                finger_angles = {
                    "Index": calculate_angle(
                        points[5], points[6], points[7]
                    ),
                    "Middle": calculate_angle(
                        points[9], points[10], points[11]
                    ),
                    "Ring": calculate_angle(
                        points[13], points[14], points[15]
                    ),
                    "Pinky": calculate_angle(
                        points[17], points[18], points[19]
                    )
                }

                # Experimental measurements.
                index_angle_3d = calculate_angle(
                    points_3d[5],
                    points_3d[6],
                    points_3d[7]
                )

                index_angle_2 = calculate_angle(
                    points[6], points[7], points[8]
                )

                index_base_angle = calculate_angle(
                    points[0], points[5], points[6]
                )

                thumb_angle = calculate_angle(
                    points[2], points[3], points[4]
                )

                thumb_direction_angle = calculate_angle(
                    points_3d[4],
                    points_3d[2],
                    points_3d[9]
                )

                # Thumb-tip to index-tip distance,
                # normalized by palm width.
                thumb_index_distance = np.linalg.norm(
                    np.array(points[4]) - np.array(points[8])
                )

                palm_width = np.linalg.norm(
                    np.array(points[5]) - np.array(points[17])
                )

                normalized_distance = None

                if palm_width > 0:
                    normalized_distance = (
                        thumb_index_distance / palm_width
                    )

                # -------------------- CLASSIFIER --------------------

                threshold = 120
                straight_fingers = sum(
                    angle is not None and angle > threshold
                    for angle in finger_angles.values()
                )

                # Keep the current rules unchanged for now.
                if straight_fingers >= 3:
                    gesture = "Open Palm"
                elif straight_fingers <= 1:
                    gesture = "Fist"
                else:
                    gesture = "Other"

                # Only the prediction is displayed.
                cv2.putText(
                    frame,
                    f"Gesture: {gesture}",
                    (10, 35 + hand_index * 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                # Draw hand connections.
                for connection in connections:
                    start = points[connection.start]
                    end = points[connection.end]

                    cv2.line(
                        frame, start, end, (255, 0, 0), 2
                    )

                # Save this hand's measurements for the M key.
                measurement_data.append({
                    "hand": hand_index + 1,
                    "finger_angles": finger_angles,
                    "straight_fingers": straight_fingers,
                    "normalized_thumb_distance": normalized_distance,
                    "thumb_direction_angle_3d": thumb_direction_angle,
                    "thumb_angle_2d": thumb_angle,
                    "index_angle_3d": index_angle_3d,
                    "index_angle_2": index_angle_2,
                    "index_base_angle": index_base_angle,
                    "gesture": gesture
                })

            # Print measurements once when requested.
            if print_measurements_next_frame:
                if measurement_data:
                    for data in measurement_data:
                        print("\n--- Hand Measurements ---")

                        for name, value in data.items():
                            print(f"{name}: {value}")
                else:
                    print("No hand detected to measure.")

                print_measurements_next_frame = False

            cv2.imshow("Hand Landmark Tracker", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("-"):
                if not trial_active or trial_done:
                    trial_active = True
                    countdown_start = time.perf_counter()
                    trial_start = None
                    trial_done = False
                    print("Trial started! Get ready...")

            elif key == ord("m"):
                print_measurements_next_frame = True

            elif key == ord("q"):
                break

finally:
    camera.release()
    cv2.destroyAllWindows()
