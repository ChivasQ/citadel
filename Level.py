import pygame.sprite


class Level:
    def __init__(self, screen):
        self.display_surface = screen
        self.floor_sprites = pygame.sprite.Group()
        self.wall_sprites = pygame.sprite.Group()

    def update(self):
        pass