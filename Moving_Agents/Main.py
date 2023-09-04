import pygame
from Vector import Vector
import Constants
from Player import Player
from Enemy import Enemy

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode(
    (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))


player = Player(Vector(screen.get_width() / 2, screen.get_height() / 2), Constants.PLAYER_SIZE, Constants.PLAYER_SPEED)
enemy = Enemy(Vector(Constants.ENEMY_START, Constants.ENEMY_START), Constants.ENEMY_SIZE, Constants.ENEMY_SPEED)


test_vector_one = Vector(300, 400)
test_vector_two = Vector(100, 150)
test_vector_three_sub = test_vector_one.__sub__(test_vector_two)
print(test_vector_three_sub)
test_vector_three_add = test_vector_one.__add__(test_vector_two)
print(test_vector_three_add)
dot_product = test_vector_one.dot(test_vector_two)
print(dot_product)
scaled_vector = test_vector_one.scale(2.0)
print(scaled_vector)
length = test_vector_one.length()
print(length)
print(test_vector_one.normalize())

while True:
    for event in pygame.event.get():
        if pygame.event == pygame.QUIT:
            pygame.quit
            quit()
    player.update()
    player.draw(screen)
    enemy.draw(screen)
    
    pygame.display.flip()
    clock.tick(Constants.FRAME_RATE)
    screen.fill(Constants.SCREEN_COLOR)
