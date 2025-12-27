import pygame
import math


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, target_pos, image, level_ref):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pygame.math.Vector2(pos)

        self.target_pos = pygame.math.Vector2(target_pos)  # Координати Ядра
        self.level = level_ref

        # Характеристики
        self.speed = 50.0  # Пікселів в секунду
        self.health = 50
        self.damage = 10
        self.attack_speed = 1.0  # Ударів в секунду
        self.attack_timer = 0

        self.is_attacking = False
        self.target_building = None  # Будівля, яку зараз гриземо

    def move(self, dt):
        # Рахуємо вектор до цілі
        direction = self.target_pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()

        # Пробуємо рухатися
        # Ми робимо це "наосліп", а потім перевіряємо колізії
        self.pos += direction * self.speed * dt
        self.rect.topleft = self.pos

        # Перевірка колізій з будівлями
        # Шукаємо, чи не вперлися ми в якусь будівлю
        collided_buildings = pygame.sprite.spritecollide(self, self.level.buildings_group, False)
        collided_entities = pygame.sprite.spritecollide(self, self.level.entities, False)
        if collided_buildings:
            self.pos -= direction * self.speed * dt
            self.rect.topleft = self.pos
        if collided_entities:
            pass

    def update(self, dt):
        if self.health <= 0:
            self.kill()
            return

        self.move(dt)