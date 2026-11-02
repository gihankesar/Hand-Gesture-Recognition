import cv2
import mediapipe as mp

camera = cv2.VideoCapture(0)

while True:
    success , frame = camera.read()

    # print(frame.shape)
    # print(frame.dtype)

    if not success:
        print("Couldnt read a frame!")
        break

    # cv2.imshow("My Webcam", frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50,150)
    # print(gray[0,0])
    # print(gray.shape)  # (480, 640)
    # print(gray.ndim)   # 2
    # print(gray.dtype)
    # cv2.imshow("Greyscale Webcam", gray)
    cv2.imshow("Orginal Webcam", frame)
    cv2.imshow("Hand Edges", edges)

    if cv2.waitKey(1) == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()