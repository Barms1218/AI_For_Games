import pygame


pygame.init()

display_width = 800
display_height = 600

game_display = pygame.display.set_mode((display_width, display_height))
square = pygame.draw.rect(game_display, (255, 0, 0), pygame.Rect(25, 25, 25, 25))
pygame.display.update()


while(True):
    for event in pygame.event.get():
        print(event)
        if event.type == pygame.QUIT:
            pygame.quit
            quit()