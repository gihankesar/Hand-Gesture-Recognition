# class Student:
#     def __init__(self, name, age):
#         self.name = name

#         if age <= 0:
#             raise ValueError("Age cannoot be negative")

#         self.age = age
#     # def introduce(self):
#     #     print(f"Hi , I'm {self.name} and {self.age} old")


#     def __str__(self):
#         return f"HY {self.name} and {self.age}"
    
# student = Student("kesara", 0)

# print(student)

# class Student:
#     def __init__(self,name):
#         self.name = name

#     @property
#     def name(self):
#         return self._name

#     @name.setter
#     def name(self, name):
#         self._name = name


# student = Student("Kesara")
# print(student.name)

# class Student:
#     students = 0

#     @classmethod
#     def count(cls):
#         return cls.students


# class Math:

#     @staticmethod
#     def add(a,b):
#         return a + b

# print(Math.add(4,3))
    

# class Animal:
#     def __init__(self,name):
#         self.name = name

# class Dog(Animal):

#     def __init__(self,name,breed):
#         super().__init__(name)
#         self.breed = breed

# dog = Dog("puppy", "german")
# print(dog.name)


# class Point:

#     def __init__(self,x,y):
#         self.x = x
#         self.y = y
#     def __add__(self,other):
#         return(
#             self.x + other.x,
#             self.y + other.y
#         )

# p1 = Point(2,3)
# p2 = Point(4,5)

# p3 = p1 + p2
# print(p3)

class Dog:

    def __init__(self, name):
        self.name = name

    def bark(self):
        print(f"{self.name} says woof!")


dog1 = Dog("Max")
dog2 = Dog("Buddy")
dog1.name = "Rocky"

dog1.bark()
dog2.bark()