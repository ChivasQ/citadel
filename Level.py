import math
import random
from random import randint

import pygame
import noise
import numpy as np
from pygame.display import update

from CameraGroup import CameraGroup
from Enemy import Enemy
from Item import Item
from Miner import Miner
from Player import Player
from Tile import Tile
from Building import Building
from Conveyor import Conveyor
from Furnace import Furnace
from Inspector import Inspector
from Core import Core
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

        self.player = Player((100, 100), self.entities, self.rm)

        self.item_textures = {
            'iron': self.rm.get_texture("resources/textures/item/raw_iron.png"),
            'copper': self.rm.get_texture("resources/textures/item/raw_copper.png"),
            'coal': self.rm.get_texture("resources/textures/item/coal.png"),
            'copper_ingot': self.rm.get_texture("resources/textures/item/copper_ingot.png")
        }

        self.core_tex = self.rm.get_texture("resources/textures/tiles/core.png", (96, 96))
        self.enemy_tex = self.rm.get_texture("resources/textures/enemy.png", (32, 32))
        self.turret_tex_base = self.rm.get_texture("resources/textures/tiles/turret.png", (32, 32))
        self.turret_tex_turret = self.rm.get_texture("resources/textures/tiles/turret_head.png", (32, 32))
        self.core_center_pos = (0, 0)
        self.inventory = {'iron': 0, 'copper': 0, 'coal': 0, 'copper_ingot': 0}

        self.build_mode = 0  # 0: Wall, 1: Miner, 2: Conveyor, 3: Furnace
        self.current_rotation = 0  # 0: Right, 1: Down, 2: Left, 3: Up

        # UI
        self.hover_surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.hover_surf, (255, 255, 255, 100), (0, 0, self.TILE_SIZE, self.TILE_SIZE), 2)

        self.load_map()

    def update_camera(self):
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

    def load_map(self):
        # Генерація руди
        ores = ['coal', 'copper']

        def get_ore(i):
            if i < len(ores):
                return ores[i]
            else:
                return None

        # Генерація мапи (32x32)
        self.ground_data = [[0 for x in range(32)] for y in range(32)]
        self.ore_data = [[get_ore(randint(0, 5)) for x in range(32)] for y in range(32)]

        self.map_width = len(self.ground_data[0])
        self.map_height = len(self.ground_data)

        # Текстури
        ground_textures = {
            0: self.rm.get_texture("resources/textures/tiles/grass.png", (32, 32)),
            1: self.rm.get_texture("resources/textures/tiles/stone.png", (32, 32))
        }

        ore_textures = {
            'iron': self.rm.get_texture("resources/textures/tiles/iron_ore.png", (32, 32)),
            'copper': self.rm.get_texture("resources/textures/tiles/copper_ore.png", (32, 32)),
            'coal': self.rm.get_texture("resources/textures/tiles/coal_ore.png", (32, 32))
        }

        # Створення тайлів
        for y in range(self.map_height):
            for x in range(self.map_width):
                pos = (x * self.TILE_SIZE, y * self.TILE_SIZE)

                # Земля
                ground_type = self.ground_data[y][x]
                Tile(pos, [self.background], ground_textures[ground_type])

                # Руда
                ore_type = self.ore_data[y][x]
                if ore_type in ore_textures:
                    Tile(pos, [self.ore_group], ore_textures[ore_type])

        core_gx, core_gy = 15, 15
        core_size = 3

        # Позиція в пікселях
        core_pos_x = core_gx * self.TILE_SIZE
        core_pos_y = core_gy * self.TILE_SIZE
        self.core_center_pos = (core_pos_x, core_pos_y)
        core_building = Core(
            (core_pos_x, core_pos_y),
            (core_gx, core_gy),
            [self.buildings_group],
            self.core_tex,
            self
        )

        for y in range(core_size):
            for x in range(core_size):
                self.world_data[(core_gx + x, core_gy + y)] = core_building

        print("Map loaded successfully")


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

    def place_building(self):
        gx, gy = self.get_grid_pos()

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
            new_building = Conveyor(
                (pos_x, pos_y), (gx, gy),
                [self.buildings_group],
                tex,
                self.current_rotation,
                self
            )
        elif self.build_mode == 3:  # Furnace
            tex = self.rm.get_texture("resources/textures/tiles/furnace.png", (32, 32))
            new_building = Furnace((pos_x, pos_y), (gx, gy), [self.buildings_group], tex, self)
        elif self.build_mode == 4:  # Turret
            # Турель 1x1, як стіна
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

        self.update_camera()

        self.background.custom_draw(self.OFFSET)  # Земля
        self.ore_group.custom_draw(self.OFFSET)  # Руда
        self.buildings_group.custom_draw(self.OFFSET)  # Будівлі
        self.items_group.custom_draw(self.OFFSET)  # Предмети
        self.entities.custom_draw(self.OFFSET)  # Гравець

        self.draw_hover()  # Курсор