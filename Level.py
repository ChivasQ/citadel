import random
from random import randint

import pygame
import noise
import numpy as np
from Item import Item
from Miner import Miner
from Player import Player
from Tile import Tile
from Building import Building
from Conveyor import Conveyor
from Furnace import Furnace
from Inspector import Inspector
from Core import Core


class Level:
    def __init__(self, screen, resource_manager):
        self.display_surface = screen
        self.rm = resource_manager

        self.TILE_SIZE = 32
        self.OFFSET = pygame.math.Vector2(0, 0)

        self.background = pygame.sprite.Group()  # Background
        self.ore_group = pygame.sprite.Group()  # Руда
        self.buildings_group = pygame.sprite.Group()  # Buildings
        self.items_group = pygame.sprite.Group()  # Предмети на конвеєрах
        self.entities = pygame.sprite.Group()  # Гравець

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

        # Текстура ядра 96x96 (3x3 клітинки)
        self.core_tex = self.rm.get_texture("resources/textures/tiles/core.png", (96, 96))

        self.inventory = {'iron': 0, 'copper': 0, 'coal': 0, 'copper_ingot': 0}

        self.build_mode = 0  # 0: Wall, 1: Miner, 2: Conveyor, 3: Furnace
        self.current_rotation = 0  # 0: Right, 1: Down, 2: Left, 3: Up

        # UI
        self.hover_surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.hover_surf, (255, 255, 255, 100), (0, 0, self.TILE_SIZE, self.TILE_SIZE), 2)

        self.load_map()

    def load_map(self):
        # Генерація руди
        ores = ['coal', 'copper']

        def get_ore(i):
            if i < len(ores):
                return ores[i]
            else:
                return None

        # Генерація масивів (32x32)
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

        # Створення тайлів (візуалізація)
        for y in range(self.map_height):
            for x in range(self.map_width):
                pos = (x * self.TILE_SIZE + self.OFFSET.x, y * self.TILE_SIZE + self.OFFSET.y)

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
        core_pos_x = core_gx * self.TILE_SIZE + self.OFFSET.x
        core_pos_y = core_gy * self.TILE_SIZE + self.OFFSET.y

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

    def get_grid_pos(self):
        mouse_pos = pygame.mouse.get_pos()
        gx = int((mouse_pos[0] - self.OFFSET.x) // self.TILE_SIZE)
        gy = int((mouse_pos[1] - self.OFFSET.y) // self.TILE_SIZE)
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

            # Видаляємо візуально
            building.kill()
            print(f"Destroyed building at {gx, gy}")

    def place_building(self):
        gx, gy = self.get_grid_pos()

        if not (0 <= gx < self.map_width and 0 <= gy < self.map_height):
            return

        if (gx, gy) in self.world_data:
            print("Cell occupied")
            return

        pos_x = gx * self.TILE_SIZE + self.OFFSET.x
        pos_y = gy * self.TILE_SIZE + self.OFFSET.y
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
            world_x = gx * self.TILE_SIZE + self.OFFSET.x
            world_y = gy * self.TILE_SIZE + self.OFFSET.y
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
        self.entities.update()

        self.background.draw(self.display_surface)  # Земля
        self.ore_group.draw(self.display_surface)  # Руда
        self.buildings_group.draw(self.display_surface)  # Будівлі
        self.items_group.draw(self.display_surface)  # Предмети (мають бути НАД будівлями)
        self.entities.draw(self.display_surface)  # Гравець

        self.draw_hover()  # Курсор