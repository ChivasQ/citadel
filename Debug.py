import pygame
pygame.init()
font = pygame.font.Font("resources/fonts/PressStart2P-Regular.ttf", 20)

def debug_text(info, x = 10, y = 10):
    display_surface = pygame.display.get_surface()
    text_surface = font.render(str(info), False, "White")
    display_surface.blit(text_surface, (x, y))