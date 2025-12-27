import pygame


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

    def custom_draw(self, camera_offset):
        for sprite in self.sprites():

            offset_pos = sprite.rect.topleft - camera_offset
            self.display_surface.blit(sprite.image, offset_pos)

            # для рендеру голови турелі
            if hasattr(sprite, 'rotating_image'):
                head_rect = sprite.rotating_image.get_rect(center=sprite.rect.center)

                head_offset_pos = head_rect.topleft - camera_offset

                self.display_surface.blit(sprite.rotating_image, head_offset_pos)