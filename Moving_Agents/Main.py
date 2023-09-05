import pygame
from Vector import Vector
import Constants
from Player import Player
from Enemy import Enemy

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode(
    (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))

enemies = list()

player = Player(Vector(Constants.SCREEN_WIDTH / 2, Constants.SCREEN_HEIGHT / 2),
                Constants.PLAYER_SIZE, Constants.PLAYER_SPEED)
enemy = Enemy(Vector(Constants.ENEMY_START, Constants.ENEMY_START),
              Constants.ENEMY_SIZE, Constants.ENEMY_SPEED)

enemies.append(enemy)

while True:
    for event in pygame.event.get():
        if pygame.event == pygame.QUIT:
            pygame.quit
            quit()
    player.update(enemies)
    player.draw(screen)
    enemy.update(player)
    enemy.draw(screen)

    pygame.display.flip()
    clock.tick(Constants.FRAME_RATE)
    screen.fill(Constants.SCREEN_COLOR)
