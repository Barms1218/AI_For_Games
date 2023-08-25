from turtle import Screen
import pygame
import time

pygame.init()

display_width = 800
display_height = 600
clock = pygame.time.Clock()

game_display = pygame.display.set_mode((display_width, display_height))

x = 400
y = 300

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