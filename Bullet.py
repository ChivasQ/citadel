import pygame


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos, groups, level_ref):
        super().__init__(groups)
        self.level = level_ref

        # Створюємо просту текстуру кулі
        self.image = pygame.Surface((8, 4))
        self.image.fill((255, 255, 0))

        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(pos)

        # Вектор руху
        direction = pygame.math.Vector2(target_pos) - self.pos
        if direction.length() > 0:
            direction = direction.normalize()

        self.velocity = direction * 400.0  # Швидкість: 400 пікселів/сек
        self.damage = 25
        self.lifetime = 2.0

        angle = direction.angle_to(pygame.math.Vector2(1, 0))
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        # Рух
        self.pos += self.velocity * dt
        self.rect.center = self.pos

        # Перевірка влучання у ворогів
        hits = pygame.sprite.spritecollide(self, self.level.entities, False)

        if hits:
            enemy = hits[0]
            if hasattr(enemy, 'health'):
                enemy.health -= self.damage
                print(f"Hit target! HP: {enemy.health}")
                self.kill()