import pygame.sprite

from Player import Player
from Tile import Tile
from Building import Building

class Level:
    def __init__(self, screen, resource_manager):
        self.display_surface = screen

        self.background = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.buildings_group = pygame.sprite.Group()

        self.rm = resource_manager
        self.player = Player((100,100), self.entities, self.rm)

        self.TILE_SIZE = 32
        self.OFFSET = pygame.math.Vector2(0, 0)

        self.world_data = {}

        self.hover_surf = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE), pygame.SRCALPHA)
        # Прямокутник виділення
        pygame.draw.rect(self.hover_surf, (255, 255, 255, 100), (0, 0, self.TILE_SIZE, self.TILE_SIZE), 2)

        self.build_tex = self.rm.get_texture("resources/textures/tiles/wall.png", (32, 32))

        self.load_map()

    def get_grid_pos(self):
        mouse_pos = pygame.mouse.get_pos()

        gx = int((mouse_pos[0] - self.OFFSET.x) // self.TILE_SIZE)
        gy = int((mouse_pos[1] - self.OFFSET.y) // self.TILE_SIZE)
        return gx, gy

    def draw_hover(self):
        gx, gy = self.get_grid_pos()

        world_x = gx * self.TILE_SIZE + self.OFFSET.x
        world_y = gy * self.TILE_SIZE + self.OFFSET.y
        self.display_surface.blit(self.hover_surf, (world_x, world_y))

    def place_building(self):
        gx, gy = self.get_grid_pos()

        if (gx, gy) in self.world_data:
            return

        pos_x = gx * self.TILE_SIZE + self.OFFSET.x
        pos_y = gy * self.TILE_SIZE + self.OFFSET.y

        # Створення об'єкта
        new_building = Building(
            (pos_x, pos_y),
            (gx, gy),
            [self.buildings_group],
            self.build_tex
        )

        self.world_data[(gx, gy)] = new_building

    def load_map(self):
        wall_tex = self.rm.get_texture("resources/textures/tiles/wall.png", (self.TILE_SIZE, self.TILE_SIZE))
        grass_tex = self.rm.get_texture("resources/textures/tiles/grass.png", (self.TILE_SIZE, self.TILE_SIZE))
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
                    pos = (x * self.TILE_SIZE + 128, y * self.TILE_SIZE + 128)
                    Tile(pos, [self.background], tile_textures[char])
        print("map loaded")


    def update(self, dt):
        self.player.tick(dt)

        self.background.draw(self.display_surface)
        self.buildings_group.draw(self.display_surface)
        self.entities.draw(self.display_surface)


        self.draw_hover()

        self.background.update()
        self.buildings_group.update()
        self.entities.update()

