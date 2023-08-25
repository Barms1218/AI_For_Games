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
    
    def __dot__(self, other):
        return self.x * other.x + self.y * other.y
        
    def __scale__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    def __length__(self):
        if self.x != 0 and self.y != 0:
            return math.sqrt(self.x**2 + self.y**2)
