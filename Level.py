import math
import random
import sys
from random import randint

import noise
import pygame

from Building import Building
from CameraGroup import CameraGroup
from Conveyor import Conveyor
from Core import Core
from Debug import debug_text
from Enemy import Enemy
from Furnace import Furnace
from Inspector import Inspector
from Item import Item
from Miner import Miner
from Player import Player
from Tile import Tile
from Turret import Turret


class Level:
    def __init__(self, screen, resource_manager):
        self.display_surface = screen
        self.rm = resource_manager

        self.TILE_SIZE = 32
        self.OFFSET = pygame.math.Vector2(0, 0)

        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        self.background = CameraGroup()  # Background
        self.ore_group = CameraGroup()  # Руда
        self.buildings_group = CameraGroup()  # Buildings
        self.items_group = CameraGroup()  # Предмети на конвеєрах
        self.entities = CameraGroup()  # Ентіті

        self.inspector = Inspector()

        # Дані карти
        self.ground_data = []
        self.ore_data = []
        self.world_data = {}
        self.map_height = 0
        self.map_width = 0

        self.player = Player((33*self.TILE_SIZE + 16, 33*self.TILE_SIZE + 16), self.entities, self.rm)

        self.item_textures = {
            'iron': self.rm.get_texture("resources/textures/item/raw_iron.png"),
            'copper': self.rm.get_texture("resources/textures/item/raw_copper.png"),
            'coal': self.rm.get_texture("resources/textures/item/coal.png"),
            'copper_ingot': self.rm.get_texture("resources/textures/item/copper_ingot.png")
        }
        self.core = None
        # TEXTURES
        self.core_tex = self.rm.get_texture("resources/textures/tiles/core.png", (96, 96))
        self.enemy_tex = self.rm.get_texture("resources/textures/enemy.png", (32, 32))
        self.turret_tex_base = self.rm.get_texture("resources/textures/tiles/turret.png", (32, 32))
        self.turret_tex_turret = self.rm.get_texture("resources/textures/tiles/turret_head.png", (32, 32))
        self.core_center_pos = (0, 0)
        self.inventory = {'iron': 0, 'copper': 0, 'coal': 0, 'copper_ingot': 0}

        self.build_mode = 0  # 0: Wall, 1: Miner, 2: Conveyor, 3: Furnace
        self.current_rotation = 0  # 0: Right, 1: Down, 2: Left, 3: Up

        # ENEMY WAVES
        self.wave_timer = 0
        self.time_between_waves = 300.0  # Час між хвилями
        self.is_wave_active = False
        self.current_wave_number = 0
        self.spawn_grid_pos = (5, 5)

        self.current_spawn_pos = (0, 0)  # Куди спавнити

        self.enemy_logic_tick = True
        # UI
        self.hover_surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.hover_surf, (255, 255, 255, 100), (0, 0, self.TILE_SIZE, self.TILE_SIZE), 2)

        self.load_map()

    def update_camera(self):
        w, h = self.display_surface.get_size()
        self.half_w = w // 2
        self.half_h = h // 2

        camera_center_x = self.OFFSET.x + self.half_w
        camera_center_y = self.OFFSET.y + self.half_h

        diff_x = self.player.rect.centerx - camera_center_x
        diff_y = self.player.rect.centery - camera_center_y

        distance = math.hypot(diff_x, diff_y)

        if distance > 50:

            move_distance = distance - 50

            shift_x = (diff_x / distance) * move_distance
            shift_y = (diff_y / distance) * move_distance

            self.OFFSET.x += shift_x
            self.OFFSET.y += shift_y

    def start_new_wave(self):
        self.current_wave_number += 1
        print(f"--- WAVE {self.current_wave_number} ---")


        base_spawn_x = self.spawn_grid_pos[0] * self.TILE_SIZE
        base_spawn_y = self.spawn_grid_pos[1] * self.TILE_SIZE

        count = 3 + (self.current_wave_number * 2)

        for i in range(count):
            offset_x = randint(-160, 160)
            offset_y = randint(-160, 160)

            spawn_pos = (
                base_spawn_x + offset_x,
                base_spawn_y + offset_y
            )

            Enemy(spawn_pos, [self.entities], self.core_center_pos, self.enemy_tex, self)

    def update_waves(self, dt):
        self.wave_timer += dt
        debug_text(int(self.wave_timer), y=150)
        if self.wave_timer >= self.time_between_waves:
            self.wave_timer = 0
            self.start_new_wave()

    def load_map(self):
        self.map_width = 64
        self.map_height = 64

        # Ініціалізація масивів
        self.ground_data = [[0 for x in range(self.map_width)] for y in range(self.map_height)]
        self.ore_data = [[None for x in range(self.map_width)] for y in range(self.map_height)]
        self.world_data = {}  # Очищуємо світ

        scale = 0.05

        seed = random.randint(0, 200)

        wall_tex = self.rm.get_texture("resources/textures/tiles/cobblestone.png", (32, 32))

        print("Generating terrain...")

        for y in range(self.map_height):
            for x in range(self.map_width):

                terrain_val = noise.pnoise2(x * 0.05,
                                            y * 0.05,
                                            octaves=6,
                                            persistence=0.5,
                                            lacunarity=2.0,
                                            base=seed)

                # Позиція в пікселях
                pos_x = x * self.TILE_SIZE
                pos_y = y * self.TILE_SIZE
                pos = (pos_x, pos_y)

                center_x, center_y = self.map_width // 2, self.map_height // 2
                distance_to_core = math.hypot(x - center_x, y - center_y)
                distance_to_spawner = math.hypot((x-y)/2 - 5, (y-x)/2 - 5)*2

                max_dist = math.hypot(center_x, center_y)
                dist_factor = min(distance_to_core, distance_to_spawner) / max_dist

                final_val = terrain_val + min(dist_factor * 1.5, 1) - 0.5
                if final_val > 0.25:

                    self.ground_data[y][x] = 1

                    new_wall = Building((pos_x, pos_y), (x, y), [self.buildings_group], wall_tex, health=250)
                    self.world_data[(x, y)] = new_wall

                else:
                    self.ground_data[y][x] = 0

                    ore_val = noise.pnoise2(x * 0.2,
                                            y * 0.2,
                                            octaves=6,
                                            persistence=0.1,
                                            lacunarity=6.0,
                                            base=seed + 100)


                    if ore_val > 0.25:
                        self.ore_data[y][x] = 'coal'
                    elif ore_val < -0.30:
                        self.ore_data[y][x] = 'copper'

        ground_textures = {
            0: self.rm.get_texture("resources/textures/tiles/grass.png", (32, 32)),
            1: self.rm.get_texture("resources/textures/tiles/stone.png", (32, 32))
        }

        ore_textures = {
            'iron': self.rm.get_texture("resources/textures/tiles/iron_ore.png", (32, 32)),
            'copper': self.rm.get_texture("resources/textures/tiles/copper_ore.png", (32, 32)),
            'coal': self.rm.get_texture("resources/textures/tiles/coal_ore.png", (32, 32))
        }

        for y in range(self.map_height):
            for x in range(self.map_width):
                pos = (x * self.TILE_SIZE, y * self.TILE_SIZE)

                g_type = self.ground_data[y][x]
                Tile(pos, [self.background], ground_textures[g_type])

                # Створення тайла руди
                o_type = self.ore_data[y][x]
                if o_type:
                    Tile(pos, [self.ore_group], ore_textures[o_type])

        found_spot = False
        start_x, start_y = self.map_width // 2, self.map_height // 2

        # просто чистимо місце під ядро
        core_gx, core_gy = start_x, start_y

        core_size = 3
        for cy in range(core_size):
            for cx in range(core_size):
                tx, ty = core_gx + cx, core_gy + cy

                # Видаляємо стіну з world_data
                if (tx, ty) in self.world_data:
                    self.world_data[(tx, ty)].kill()  # Видаляємо спрайт
                    del self.world_data[(tx, ty)]  # Видаляємо з даних

                # Прибираємо руду
                self.ore_data[ty][tx] = None

        # Створюємо Ядро
        core_pos_x = core_gx * self.TILE_SIZE
        core_pos_y = core_gy * self.TILE_SIZE
        self.core_center_pos = (core_pos_x, core_pos_y)

        self.core = Core(
            (core_pos_x, core_pos_y),
            (core_gx, core_gy),
            [self.buildings_group],
            self.core_tex,
            self
        )

        for y in range(core_size):
            for x in range(core_size):
                self.world_data[(core_gx + x, core_gy + y)] = self.core

        print("Map generated procedurally!")

    def spawnEnemy(self):
        Enemy((-50, -50), [self.entities], self.core_center_pos, self.enemy_tex, self)

    def get_grid_pos(self):
        mouse_pos = pygame.mouse.get_pos()
        world_mouse_x = mouse_pos[0] + self.OFFSET.x
        world_mouse_y = mouse_pos[1] + self.OFFSET.y
        gx = int(world_mouse_x // self.TILE_SIZE)
        gy = int(world_mouse_y // self.TILE_SIZE)
        return gx, gy

    def rotate_building(self):
        self.current_rotation = (self.current_rotation + 1) % 4
        print(f"Rotation: {self.current_rotation}")

    def destroy_building(self):
        gx, gy = self.get_grid_pos()

        if (gx, gy) in self.world_data:
            building = self.world_data[(gx, gy)]

            if isinstance(building, Core):
                return

            if hasattr(building, 'size') and building.size > 1:
                start_gx, start_gy = building.grid_pos
                for y in range(building.size):
                    for x in range(building.size):
                        target = (start_gx + x, start_gy + y)
                        if target in self.world_data:
                            del self.world_data[target]
            else:
                del self.world_data[(gx, gy)]

            # Видаляємо
            building.kill()
            print(f"Destroyed building at {gx, gy}")

    def place_building(self, override_pos=None, override_rot=None):
        if override_pos is None:
            gx, gy = self.get_grid_pos()
        else:
            gx, gy = override_pos

        if not (0 <= gx < self.map_width and 0 <= gy < self.map_height):
            return

        if (gx, gy) in self.world_data:
            return

        pos_x = gx * self.TILE_SIZE
        pos_y = gy * self.TILE_SIZE
        new_building = None

        # Логіка вибору будівлі
        if self.build_mode == 0:  # Wall
            tex = self.rm.get_texture("resources/textures/tiles/wall.png", (32, 32))
            new_building = Building((pos_x, pos_y), (gx, gy), [self.buildings_group], tex)

        elif self.build_mode == 1:  # Miner
            ore_type = self.ore_data[gy][gx]
            tex = self.rm.get_texture("resources/textures/tiles/basic-miner.png", (32, 32))
            # Передаємо self (Level), щоб майнер міг спавнити предмети
            new_building = Miner((pos_x, pos_y), (gx, gy), [self.buildings_group], tex, ore_type, self)

        elif self.build_mode == 2:  # Conveyor
            tex = self.rm.get_texture("resources/textures/tiles/basic_conveyor.png", (32, 32))
            # Передаємо напрямок і self
            rot = None
            if override_rot is None:
                rot = self.current_rotation
            else:
                rot = override_rot

            new_building = Conveyor(
                (pos_x, pos_y), (gx, gy),
                [self.buildings_group],
                tex,
                rot,
                self
            )

        elif self.build_mode == 3:  # Furnace
            tex = self.rm.get_texture("resources/textures/tiles/furnace.png", (32, 32))
            new_building = Furnace((pos_x, pos_y), (gx, gy), [self.buildings_group], tex, self)
        elif self.build_mode == 4:  # Turret
            new_building = Turret((pos_x, pos_y), (gx, gy), [self.buildings_group], self.turret_tex_base, self.turret_tex_turret, self)

        # Реєстрація будівлі
        if new_building:
            self.world_data[(gx, gy)] = new_building
            print(f"Placed building mode {self.build_mode} at {gx, gy}")

    def spawn_item(self, pos, item_type):
        if item_type in self.item_textures:
            Item(pos, item_type, self.item_textures[item_type], [self.items_group])

    def draw_hover(self):
        gx, gy = self.get_grid_pos()
        if 0 <= gx < self.map_width and 0 <= gy < self.map_height:
            world_x = gx * self.TILE_SIZE - self.OFFSET.x
            world_y = gy * self.TILE_SIZE - self.OFFSET.y
            self.display_surface.blit(self.hover_surf, (world_x, world_y))

            building = self.world_data.get((gx, gy))

            if building:
                mouse_pos = pygame.mouse.get_pos()
                self.inspector.draw(self.display_surface, mouse_pos, building)

    def update(self, dt):
        self.player.tick(dt)
        # self.background.update()
        self.buildings_group.update(dt)
        self.items_group.update(dt)
        self.entities.update(dt)
        self.update_waves(dt)
        self.update_camera()

        self.background.custom_draw(self.OFFSET)  # Земля
        self.ore_group.custom_draw(self.OFFSET)  # Руда
        self.buildings_group.custom_draw(self.OFFSET)  # Будівлі
        self.items_group.custom_draw(self.OFFSET)  # Предмети
        self.entities.custom_draw(self.OFFSET)  # Гравець

        self.draw_hover()  # Курсор

        if self.core is not None:
            if self.core.health <= 0:
                print("GAME OVER: Core Destroyed!")
                pygame.quit()
                sys.exit()