import pygame
from Vector import Vector
import Constants
from Player import Player

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode(
    (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))
screen.fill(Constants.SCREEN_COLOR)

player = Player(Vector(screen.get_width() / 2, screen.get_height() / 2), 25, 1)

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
    player.draw(screen)
    clock.tick(60)
    pygame.display.update()
