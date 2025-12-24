import pygame.sprite

from Player import Player
from Tile import Tile


class Level:
    def __init__(self, screen, resource_manager):
        self.display_surface = screen
        self.background = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.rm = resource_manager
        self.player = Player((100,100), self.entities)

        self.load_map()

    def load_map(self):
        TILE_SIZE = 32
        wall_tex = self.rm.get_texture("resources/textures/tiles/wall.png", (TILE_SIZE, TILE_SIZE))
        grass_tex = self.rm.get_texture("resources/textures/tiles/grass.png", (TILE_SIZE, TILE_SIZE))
        tile_textures = {
            "1": wall_tex,
            "0": grass_tex,
        }

        level_map = [
            "111111",
            "100001",
            "101101",
            "100001",
            "111111",
        ]

        for y, row in enumerate(level_map):
            for x, cell in enumerate(row):
                char = level_map[y][x]
                if char in tile_textures:
                    pos = (x * TILE_SIZE + 100, y * TILE_SIZE + 100)
                    Tile(pos, [self.background], tile_textures[char])
        print("map loaded")


    def update(self, dt):
        self.player.tick(dt)
        self.background.draw(self.display_surface)
        self.entities.draw(self.display_surface)
        self.walls.draw(self.display_surface)

        self.background.update()
        self.entities.update()
        self.walls.update()
