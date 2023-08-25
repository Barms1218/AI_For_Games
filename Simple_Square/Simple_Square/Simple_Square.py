from turtle import Screen
import pygame
import time
import cmath

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
        return cmath.sqrt(self.x**2 + self.y**2)

pygame.init()

display_width = 800
display_height = 600
clock = pygame.time.Clock()

game_display = pygame.display.set_mode((display_width, display_height))

x = 400
y = 300

first_vector = Vector(x, y)
second_vector = Vector(100, 50)

third_vector = Vector.__dot__(first_vector, second_vector)
length = Vector.__length__(first_vector)
print(length)

while(True):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit
            quit()
        keys = pygame.key.get_pressed()
        up = keys[pygame.K_w]
        down = keys[pygame.K_s]
        left = keys[pygame.K_a]
        right = keys[pygame.K_d]
        if up:
            y = y - 1
        if down:
            y = y + 1
        if left:
            x = x - 1
        if right:
            x = x + 1
        square = pygame.draw.rect(game_display, (255, 0, 0), pygame.Rect(x, y, 25, 25))
        pygame.display.flip()
        clock.tick(60)
        game_display.fill((100, 149, 237))