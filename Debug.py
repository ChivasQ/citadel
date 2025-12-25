import pygame
pygame.init()
font = pygame.font.Font("resources/fonts/PressStart2P-Regular.ttf", 20)

text = []

def debug_text(info, x = 10, y = 10):
    text.append((info, x, y))

def render():
    display_surface = pygame.display.get_surface()
    for i in text:
        info, x, y = i
        text_surface = font.render(str(info), False, "White")
        display_surface.blit(text_surface, (x, y))
    text.clear()