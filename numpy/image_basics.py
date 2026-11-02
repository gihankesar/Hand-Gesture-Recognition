import cv2
import numpy as np

# image = np.zeros((100,100, 3), dtype=np.uint8)

# print("Shape:" , image.shape)
# print("Dimentions:" , image.ndim)
# print("Data type: ", image.dtype)
# print("First pixel: ", image[0,0])

# cv2.imshow("My First Image", image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

image = np.zeros((400,400,3), dtype=np.uint8)
image[50:200, 50:200] = [0, 0, 255]

cv2.imshow("My first color image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()