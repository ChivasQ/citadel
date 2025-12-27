import pygame

from Debug import addLine
from Pathfinding import Pathfinding


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, core_pos, image, level_ref):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pygame.math.Vector2(pos)

        self.level = level_ref

        self.core_pos = pygame.math.Vector2(core_pos)

        # Поточна ціль (спочатку це Ядро)
        self.target_pixel_pos = pygame.math.Vector2(core_pos)
        self.target_grid_pos = (
            int(core_pos[0] // self.level.TILE_SIZE),
            int(core_pos[1] // self.level.TILE_SIZE)
        )

        self.speed = 50.0
        self.health = 50
        self.damage = 10
        self.attack_speed = 1.0
        self.attack_timer = 0

        self.path = []
        self.path_timer = 0
        self.current_path_target = None

        self.is_attacking = False
        self.target_building = None

    def get_grid_pos(self):
        return (
            int(self.pos.x // self.level.TILE_SIZE),
            int(self.pos.y // self.level.TILE_SIZE)
        )

    def select_target(self):
        closest_turret = None
        min_dist = float('inf')

        for building in self.level.buildings_group:
            if building.__class__.__name__ == 'Turret':

                dist = self.pos.distance_to(pygame.math.Vector2(building.rect.center))

                if dist < min_dist:
                    min_dist = dist
                    closest_turret = building

        if closest_turret:
            # Йдемо до турелі
            self.target_pixel_pos = pygame.math.Vector2(closest_turret.rect.center)
        else:
            # Турелей немає то йдемо до Ядра
            self.target_pixel_pos = self.core_pos

        # Оновлюємо координати сітки для A*
        self.target_grid_pos = (
            int(self.target_pixel_pos.x // self.level.TILE_SIZE),
            int(self.target_pixel_pos.y // self.level.TILE_SIZE)
        )

    def calculate_path(self):
        start = self.get_grid_pos()

        if start == self.target_grid_pos:
            self.path = []
            return

        new_path = Pathfinding.get_path(
            start,
            self.target_grid_pos,
            self.level.world_data,
            self.level.map_width,
            self.level.map_height
        )

        if new_path:
            self.path = new_path
            if len(self.path) > 0:
                self.path.pop(0)

    def move(self, dt):
        self.path_timer += dt

        # Оновлюємо шлях та ціль кожні 0.5 секунди
        if self.path_timer > 0.5:
            self.path_timer = 0

            self.select_target()

            self.calculate_path()

        direction = pygame.math.Vector2(0, 0)

        # Якщо є шлях, йдемо до наступної точки шляху
        if self.path:
            next_node = self.path[0]
            target_pixel_x = next_node[0] * self.level.TILE_SIZE
            target_pixel_y = next_node[1] * self.level.TILE_SIZE

            target_vec = pygame.math.Vector2(target_pixel_x, target_pixel_y)
            direction = target_vec - self.pos

            # Якщо ми дуже близько до точки, переходимо до наступної
            if direction.length() < 5:
                self.pos = target_vec
                self.path.pop(0)
                return

        else:
            # Якщо A* не знайшов шлях або ми близько -> йдемо напряму
            direction = self.target_pixel_pos - self.pos

        if direction.length() > 0:
            direction = direction.normalize()

        self.pos += direction * self.speed * dt
        self.rect.topleft = self.pos

        # Перевірка на зіткнення з будівлями
        collided_buildings = pygame.sprite.spritecollide(self, self.level.buildings_group, False)

        if collided_buildings:
            self.pos -= direction * self.speed * dt
            self.rect.topleft = self.pos

            self.is_attacking = True
            self.target_building = collided_buildings[0]
        else:
            self.is_attacking = False
            self.target_building = None

    def attack(self, dt):
        if not self.target_building:
            self.is_attacking = False
            return

        self.attack_timer += dt
        if self.attack_timer >= 1.0 / self.attack_speed:
            self.attack_timer = 0

            if hasattr(self.target_building, 'health'):
                self.target_building.health -= self.damage
                print(f"Enemy hit building! HP: {self.target_building.health}")

                if self.target_building.health <= 0:
                    self.target_building.kill()

                    grid_pos = self.target_building.grid_pos
                    if hasattr(self.target_building, 'size') and self.target_building.size > 1:
                        start_gx, start_gy = grid_pos
                        for y in range(self.target_building.size):
                            for x in range(self.target_building.size):
                                t = (start_gx + x, start_gy + y)
                                if t in self.level.world_data:
                                    del self.level.world_data[t]
                    elif grid_pos in self.level.world_data:
                        del self.level.world_data[grid_pos]

                    self.target_building = None
                    self.is_attacking = False

                    # Примусово оновлюємо ціль і шлях, бо будівля зникла
                    self.select_target()
                    self.calculate_path()

    def draw_path(self):
        if not self.path:
            return
        start_point = self.rect.center
        tile_size = self.level.TILE_SIZE
        half_tile = tile_size // 2
        for node in self.path:
            target_x = node[0] * tile_size + half_tile
            target_y = node[1] * tile_size + half_tile
            end_point = (target_x, target_y)
            addLine(start_point[0], start_point[1], end_point[0], end_point[1], 1)
            start_point = end_point

    def update(self, dt):
        if self.health <= 0:
            self.kill()
            return

        if self.is_attacking:
            self.attack(dt)
        else:
            self.move(dt)

        self.draw_path()