import pygame

class Building(pygame.sprite.Sprite):
    def __init__(self, pos, grid_pos, groups, image, health=100):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.grid_pos = grid_pos
        self.health = health

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.kill()