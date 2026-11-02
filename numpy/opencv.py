# import cv2
# import numpy as np

# print("OpenCV:", cv2.__version__)
# print("NumPy:", np.__version__)


# import mediapipe as mp

# print("MediaPipe version:", mp.__version__)
# print("Has solutions:", hasattr(mp, "solutions"))
# print("Has tasks:", hasattr(mp, "tasks"))

import numpy as np

A = (100, 200)
B = (150, 200)
C = (150, 150)
# angle_rad = np.arccos(0)
# angle_deg = np.degrees(angle_rad)

# print(angle_deg)


def calculate_angle(A, B, C):
    A_ = np.array(A)
    B_ = np.array(B)
    C_ = np.array(C)
    new = A_ - B_
    new2 = C_ - B_

    dot_prodcut = np.dot(new, new2)
    length1 = np.linalg.norm(new)
    length2 = np.linalg.norm(new2)
    
    if length1 == 0 or length2 == 0:
        return None
    
    cosine_value = dot_prodcut / (length1 * length2)
    
    angle_rad = np.arccos(np.clip(cosine_value, -1.0, 1.0))
    angle_deg = np.degrees(angle_rad)
    return angle_deg

print(calculate_angle((100, 200), (150, 200), (200, 200)))
print(calculate_angle((100, 200), (150, 200), (150, 150)))
print(calculate_angle((100, 200), (150, 200), (100, 200)))