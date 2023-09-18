import math


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def scale(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        if self.length() == 0:
            return Vector(0, 0)
        else:
            return Vector(self.x / self.length(), self.y / self.length())
        
    def rotate(self, angle_degrees):
    # Convert the angle to radians
        angle_radians = math.radians(angle_degrees)

        # Calculate the new x and y components after rotation
        new_x = self.x * math.cos(angle_radians) - self.y * math.sin(angle_radians)
        new_y = self.x * math.sin(angle_radians) + self.y * math.cos(angle_radians)

        # Update the vector's components with the rotated values
        self.x = new_x
        self.y = new_y

    def normalize_ip(self):
        length = self.length()
        if length != 0:
            self.x /= length
            self.y /= length

    def zero():
        return Vector(0.0, 0.0)

    def one():
        return Vector(1.0, 1.0)
