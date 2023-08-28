import pygame
from Vector import Vector
import Game_Numbers

class Player:
   def __init__(self, position, velocity, size, color):
      self.position = position
      self.velocity = velocity
      self.size = size
      self.color = color
   
   def draw(self, screen):
      pygame.draw.rect(screen, self.color, pygame.Rect(self.position.x, self.position.y, self.size, self.size))
       
   def update(self):
        keys = pygame.key.get_pressed()
        up = keys[pygame.K_w]
        down = keys[pygame.K_s]
        left = keys[pygame.K_a]
        right = keys[pygame.K_d]
        if up:
            self.position.y = self.position.y - 1
        if down:
            self.position.y = self.position.y + 1
        if left:
            self.position.x = self.position.x - 1
        if right:
            self.position.x = self.position.x + 1
      
