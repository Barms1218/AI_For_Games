import pygame
from Vector import Vector
import Constants
from Player import Player
from Enemy import Enemy
import random

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode(
    (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))

enemies = list()
first_tick = pygame.time.get_ticks()
player = Player(Vector(Constants.SCREEN_WIDTH * 0.75, Constants.SCREEN_HEIGHT * 0.75),
                Constants.PLAYER_SIZE, Constants.PLAYER_SPEED)
for i in range(10):
    enemy = Enemy(Vector(random.randint(100, 700), random.randint(100, 500)),
                  Constants.ENEMY_SIZE, Constants.ENEMY_SPEED)
    enemies.append(enemy)


while True:
    for event in pygame.event.get():
        if pygame.event == pygame.QUIT:
            pygame.quit
            quit()
    tick = pygame.time.get_ticks()
    delta_time = (tick - first_tick) / 1000
    first_tick = tick
    player.update(enemies, delta_time)
    player.draw(screen)
    for enemy in enemies:
        enemy.update(player, delta_time)
        enemy.draw(screen)
    pygame.display.flip()
    clock.tick(Constants.FRAME_RATE)
    screen.fill(Constants.SCREEN_COLOR)
