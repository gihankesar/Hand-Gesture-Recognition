import numpy as np

# my_list = [1, 2, 3, 4]

# my_list = my_list * 2 wrong

# array = np.array([1,2,3,4])

# array = array * 2


# print(array)

# array = np.array([[["A", "B", "C"],["D", "E", "r"]],
#                   [["A1", "B1", "C1"],["D1", "E1", "r1"]],
#                   [["A2", "B2", "C2"],["D2", "E2", "r2"]]])


# print(array.ndim) number of dimention
# print(array.shape) shape of array

# word = array[0,0,1] + array[0,1,1] + array[0,1,0]
# print(word)

# array = np.array([[1,2,3,4],
#                  [5,6,7,8],
#                  [9,10,11,12],
#                  [13,14,15,16]])

#array[start : end : step]

# print(array[ 0: 2, 2 :])



# a = np.array([
#     [10, 20, 30],
#     [40, 50, 60]
# ])

# print(a[0:2,0:2])

# a = np.array([1, 2, 3])

# print(a.shape)
# print(a.reshape(1,3).shape)

# data = np.array([
#     [2, 4, 5],
#     [8, 10, 12],
#     [14, 16, 18]
# ])
# print(np.mean(data, axis = 0))
# print(np.mean(max, axis = 0))
# print(np.max(data, axis = 0))
# print(np.max(data, axis = 1))
# print(np.sum(data, axis = 1))

# a = np.array([1,2,3,4,5,6])

# print(a.shape)

# b = a.reshape(2,3)

# print(b)
# print(b.shape)
# print(a.reshape(2,-1))

# a = np.array([
#     [1, 2, 3],
#     [4, 5, 6]
# ])

# print(a.flatten())

# image = np.zeros((100, 200, 3), dtype=np.uint8)
# print(image)

# rng = np.random.default_rng()
#rng = np.random.default_rng(42)
# numbers = rng.random(size=(2,3))
# numbers = rng.random(size=5)
# arrays = rng.integers(0,256, size =(3,4),dtype=np.uint8)
# print(numbers)

# image = np.array([
#     [50,100],
#     [150,200]
# ], dtype=np.uint8)
# pixel = np.array([240, 100, 20], dtype=np.uint8)
# safe = pixel.astype(np.int16) + 30
# print(safe)
# brighter =np.clip(safe, 0 , 255)
# print(brighter)

# pixels = np.array([0, 64 ,128, 255], dtype=np.uint8)
# normalized = pixels / 255.0
# print(normalized)
# color brighter with loop
# for i in range(len(pixels)):
    # pixels[i] = pixel[i] + 30


# image = np.array([
#     [10, 80, 150],
#     [200, 40, 255]
# ], dtype=np.uint8)

# mask = image > 100
# bright_pixels = image[mask]
# print(bright_pixels)

# a = np.array([5, 10, 15, 20])

# b = a[1:3]
# b[1] = 99

# print(a)

# a = np.array([[[10, 20, 30]]])
# print(a.shape)

# b = np.squeeze(a)
# print(b.shape)

# a = np.array([[1, 2],
#               [3, 4]])

# b = np.array([[5, 6],
#               [7, 8]])

# c = np.concatenate((a, b), axis=1)


# a = np.array([10, 20, 30])
# b = np.array([40, 50, 60])

# c = np.stack((a, b), axis=0)
# a = np.array([1, 2, 3])
# b = np.array([4, 5, 6])

# c = np.concatenate((a, b))
# d = np.stack((a, b), axis=1)
# print(c)
# print(c.shape)