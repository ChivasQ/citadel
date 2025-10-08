import pygame.sprite

from Debug import debug_text


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        self.original_image = pygame.image.load("resources/textures/player.png").convert_alpha()
        self.image = self.original_image
        self.pos = pos
        self.rect = self.image.get_rect(center=pos)

        self.speed = 0.1
        self.direction = pygame.math.Vector2()
        self.angle = 0

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def player_rotate(self):
        if self.direction.length_squared() > 0:
            self.angle = self.direction.angle_to(pygame.Vector2(0, -1))

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move(self):
        self.pos += self.direction * self.speed # TODO: add delta time
        self.rect.center = self.pos
        debug_text(self.direction * self.speed, 5, 40)
        debug_text(self.pos, 5, 70)

    def tick(self):
        self.input()
        self.player_rotate()
        self.move()
