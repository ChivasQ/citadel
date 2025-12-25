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
        }
        self.inventory = {'iron': 0, 'copper': 0, 'coal':0}

        self.build_mode = 0  # 0: Wall, 1: Miner, 2: Conveyor
        self.current_rotation = 0  # 0: Right, 1: Down, 2: Left, 3: Up

        # UI
        self.hover_surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.hover_surf, (255, 255, 255, 100), (0, 0, self.TILE_SIZE, self.TILE_SIZE), 2)

        self.load_map()


    def load_map(self):
        ores = ['coal', 'copper']
        def get_ore(i):
            if i < len(ores):
                return ores[i]
            else: None
        # 0 - Камінь, 1 - Трава
        self.ground_data = [[0 for x in range(32)] for y in range(32)]

        self.ore_data = [[get_ore(randint(0,5)) for x in range(32)] for y in range(32)]

        self.map_width = len(self.ground_data[0])
        self.map_height = len(self.ground_data)

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
                pos = (x * self.TILE_SIZE + self.OFFSET.x, y * self.TILE_SIZE + self.OFFSET.y)

                # Земля
                ground_type = self.ground_data[y][x]
                Tile(pos, [self.background], ground_textures[ground_type])

                # Руда
                ore_type = self.ore_data[y][x]
                if ore_type in ore_textures:
                    Tile(pos, [self.ore_group], ore_textures[ore_type])

        print("Map loaded successfully")

    def get_grid_pos(self):
        mouse_pos = pygame.mouse.get_pos()
        gx = int((mouse_pos[0] - self.OFFSET.x) // self.TILE_SIZE)
        gy = int((mouse_pos[1] - self.OFFSET.y) // self.TILE_SIZE)
        return gx, gy

    def rotate_building(self):
        self.current_rotation = (self.current_rotation + 1) % 4

        gx, gy = self.get_grid_pos()

        print(f"Rotation: {self.current_rotation}")

    def destroy_building(self):
        gx, gy = self.get_grid_pos()

        if (gx, gy) in self.world_data:
            building = self.world_data[(gx, gy)]

            # Видаляємо візуально
            building.kill()

            del self.world_data[(gx, gy)]

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