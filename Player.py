import pygame.sprite

from Debug import debug_text


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, resource_manager):
        super().__init__(groups)

        self.original_image = resource_manager.get_texture("resources/textures/player.png", (32, 34)).convert_alpha()

        self.image = self.original_image
        self.pos = pos
        self.rect = self.image.get_rect(center=pos)

        self.speed = 300 # pixels per second(I think so)
        self.direction = pygame.math.Vector2()
        self.angle = 0

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.y = 0
        self.direction.x = 0

        if keys[pygame.K_w]:
            self.direction.y += -1
        if keys[pygame.K_s]:
            self.direction.y += 1
        if keys[pygame.K_d]:
            self.direction.x += 1
        if keys[pygame.K_a]:
            self.direction.x += -1




    def player_rotate(self):
        if self.direction.length_squared() > 0:
            self.angle = self.direction.angle_to(pygame.Vector2(0, -1))

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move(self, dt):
        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()

        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
        debug_text(f'DIR:{self.direction}', 10, 40)
        debug_text(f'POS:{self.pos}', 10, 70)

    def tick(self, dt):
        self.input()
        self.player_rotate()
        self.move(dt)
