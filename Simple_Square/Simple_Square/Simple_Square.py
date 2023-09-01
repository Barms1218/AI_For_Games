from turtle import Screen, screensize
import pygame
from Vector import Vector
import Game_Numbers
from Player import Player

pygame.init()

clock = pygame.time.Clock()

game_display = pygame.display.set_mode(
    (Game_Numbers.screen_size.x, Game_Numbers.screen_size.y))

player = Player(Vector(Game_Numbers.screen_width / 2, Game_Numbers.screen_height / 2),
                Game_Numbers.player_size, Game_Numbers.player_color)

while (True):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit
            quit()
        player.update()
        player.draw(game_display)

        pygame.display.flip()
        clock.tick(Game_Numbers.frame_rate)
        game_display.fill(Game_Numbers.screen_color)
