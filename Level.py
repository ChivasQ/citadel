import pygame.sprite

from Player import Player


class Level:
    def __init__(self, screen):
        self.display_surface = screen
        self.sprites = pygame.sprite.Group()
        self.wall_sprites = pygame.sprite.Group()

        self.player = Player((100,100), [self.sprites])


    def update(self, dt):
        self.player.tick(dt)
        self.sprites.draw(self.display_surface)
        self.sprites.update()
