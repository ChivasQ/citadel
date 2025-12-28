import pygame


class Item(pygame.sprite.Sprite):
    def __init__(self, pos, item_type, image, groups):
        super().__init__(groups)
        self.item_type = item_type
        self.image = pygame.transform.scale(image, (16, 16))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)

    def update(self, dt):
        self.rect.center = self.pos

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.item_type == other.item_type
        return False