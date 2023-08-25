from turtle import Screen, screensize
import pygame
import math
import Vector
import Game_Numbers
import Player

pygame.init()

clock = pygame.time.Clock()

game_display = pygame.display.set_mode((Game_Numbers.screen_size.x, Game_Numbers.screen_size.y))

x = 400
y = 300

while(True):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit
            quit()
        Player.update()
        Player.draw(game_display)
        #square = pygame.draw.rect(game_display, Game_Numbers.player_color, 
                                  #pygame.Rect(x, y, Game_Numbers.player_size, Game_Numbers.player_size))
        pygame.display.update()
        clock.tick(Game_Numbers.frame_rate)
        game_display.fill(Game_Numbers.screen_color)