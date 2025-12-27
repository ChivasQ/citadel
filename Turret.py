import pygame
import math
from Building import Building
from Bullet import Bullet

class Turret(Building):
    def __init__(self, pos, grid_pos, groups, image, rotating_image, level_ref):
        super().__init__(pos, grid_pos, groups, image)
        self.level = level_ref

        self.original_image = rotating_image
        self.rotating_image = rotating_image
        self.head_rect = self.rotating_image.get_rect(center=self.rect.center)
        # Параметри стрільби
        self.range = 200
        self.reload_time = 0.5
        self.shoot_timer = 0

        # Інвентар
        self.ammo = 0
        self.max_ammo = 20
        self.ammo_type = 'copper_ingot'

        self.target = None

    def accept_item(self, item):
        if item.item_type == self.ammo_type:
            if self.ammo < self.max_ammo:
                self.ammo += 1
                item.kill()
                return True
        return False

    def find_target(self):
        closest_enemy = None
        min_dist = self.range

        center_pos = pygame.math.Vector2(self.rect.center)

        for enemy in self.level.entities:
            if enemy == self.level.player:
                continue
            if hasattr(enemy, 'health'):
                dist = center_pos.distance_to(enemy.pos)
                if dist < min_dist:
                    min_dist = dist
                    closest_enemy = enemy

        return closest_enemy

    def rotate_towards(self, target_pos):
        dx = target_pos.x - self.rect.centerx
        dy = target_pos.y - self.rect.centery

        angle = -math.degrees(math.atan2(dy, dx))

        self.rotating_image = pygame.transform.rotate(self.original_image, angle)
        self.head_rect = self.rotating_image.get_rect(center=self.rect.center)

    def update(self, dt):
        self.shoot_timer += dt

        if self.target and (not self.target.alive() or
                            pygame.math.Vector2(self.rect.center).distance_to(self.target.pos) > self.range):
            self.target = None

        if not self.target:
            self.target = self.find_target()

        if self.target:
            # Поворот
            self.rotate_towards(self.target.pos)

            if self.ammo > 0 and self.shoot_timer >= self.reload_time:
                self.shoot()
                self.shoot_timer = 0

    def shoot(self):
        self.ammo -= 1

        Bullet(self.rect.center, self.target.pos, [self.level.entities], self.level)

    def get_info(self):
        info = super().get_info()
        info.append(f"Ammo: {self.ammo}/{self.max_ammo} ({self.ammo_type})")
        if self.target:
            info.append("Status: Targeting")
        else:
            info.append("Status: Scanning")
        return info