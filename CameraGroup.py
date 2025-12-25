import pygame


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    def custom_draw(self, camera_offset):
        for sprite in self.sprites():
            # Віднімаємо зміщення камери від позиції спрайта
            offset_pos = sprite.rect.topleft - camera_offset

            self.display_surface.blit(sprite.image, offset_pos)