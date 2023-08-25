import pygame
import Vector
import Game_Numbers

class Player:
   def __init__(self, position, velocity, size):
      self.position = position
      self.velocity = velocity
      self.size = size
   
   def draw(self, screen):
      pygame.draw.rect(screen, Game_Numbers.player_color, 
                       pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y))
       
   def update(self):
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
      
