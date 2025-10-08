import pygame.sprite

from Player import Player
from Tile import Tile


class Level:
    def __init__(self, screen):
        self.display_surface = screen
        self.background = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()

        self.player = Player((100,100), self.entities)

        self.load_map()

    def load_map(self):
        TILE_SIZE = 64
        tile_textures = {
            "1": pygame.image.load("resources/textures/tiles/wall.png"),
            "0": pygame.image.load("resources/textures/tiles/grass.png"),
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
                pos_x = x * TILE_SIZE
                pos_y = y * TILE_SIZE
                Tile((pos_x+100, pos_y+100), [self.background], tile_textures.get(level_map[y][x]))
        print("map loaded")


    def update(self, dt):
        self.player.tick(dt)
        self.background.draw(self.display_surface)
        self.entities.draw(self.display_surface)
        self.walls.draw(self.display_surface)

        self.background.update()
        self.entities.update()
        self.walls.update()
