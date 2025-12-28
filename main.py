import pygame

import Debug
from Debug import addDebugText, renderLines
from Debug import renderDebugText
from Level import Level
from ResourceManager import ResourceManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.resource_manager = ResourceManager()
        self.level = Level(self.screen, self.resource_manager)

        self.is_dragging = False
        self.drag_start_pos = None
        self.axis_drag_end_pos = None

        pygame.display.set_caption("game")
        self.clock = pygame.time.Clock()

    def close(self):
        pass

    def run(self):
        isRunning = True
        dt = 0.0
        while isRunning:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    isRunning = False
                    self.close()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # ЛКМ
                        gx, gy = self.level.get_grid_pos()
                        self.drag_start_pos = (gx, gy)
                        self.is_dragging = True

                    if event.button == pygame.BUTTON_RIGHT:
                        self.level.destroy_building()
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.is_dragging:
                        curr_gx, curr_gy = self.level.get_grid_pos()
                        start_gx, start_gy = self.drag_start_pos

                        dx = curr_gx - start_gx
                        dy = curr_gy - start_gy

                        if abs(dx) > abs(dy):
                            rotation = 0 if dx > 0 else 2

                            step = 1 if dx >= 0 else -1

                            for x in range(start_gx, curr_gx + step, step):
                                self.level.place_building((x, start_gy), rotation)

                        else:
                            rotation = 1 if dy > 0 else 3

                            step = 1 if dy >= 0 else -1

                            for y in range(start_gy, curr_gy + step, step):
                                self.level.place_building((start_gx, y), rotation)

                        self.is_dragging = False
                        self.drag_start_pos = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: self.level.build_mode = 0  # Wall
                    if event.key == pygame.K_2: self.level.build_mode = 1  # Miner
                    if event.key == pygame.K_3: self.level.build_mode = 2  # Conveyor
                    if event.key == pygame.K_4: self.level.build_mode = 3  # Furnace
                    if event.key == pygame.K_5: self.level.build_mode = 4  # Turret

                    if event.key == pygame.K_p: self.level.spawnEnemy()
                    if event.key == pygame.K_l:
                        self.level.wave_timer = self.level.time_between_waves
                    if event.key == pygame.K_r:  # Rotate
                        self.level.rotate_building()


            self.update(dt)
            dt = self.clock.tick(0) / 1000



    def start_frame(self):
        self.screen.fill("blue")

    def end_frame(self):
        renderDebugText()
        renderLines(self.level.OFFSET)
        pygame.display.update()


    def update(self, dt):
        self.start_frame()

        self.level.update(dt)
        addDebugText(f'FPS: {round(self.clock.get_fps(), 1)} DT: {dt}')

        debug_a = {
            0: "Right", 1: "Down", 2: "Left", 3: "Up"
        }

        if self.level.build_mode == 0:
            addDebugText(f'selected item: Wall', 10, 100)
        elif self.level.build_mode == 1:
            addDebugText(f'selected item: Miner', 10, 100)
        elif self.level.build_mode == 2:
            addDebugText(f'selected item: Conveyor, rotation: {debug_a[self.level.current_rotation]}', 10, 100)
        elif self.level.build_mode == 3:
            addDebugText(f'selected item: Furnace', 10, 100)
        elif self.level.build_mode == 4:
            addDebugText(f'selected item: Turret', 10, 100)
        else:
            addDebugText(f'selected item: None', 10, 100)

        if self.is_dragging and self.drag_start_pos:
            curr_gx, curr_gy = self.level.get_grid_pos()
            start_gx, start_gy = self.drag_start_pos

            dx = abs(curr_gx - start_gx)
            dy = abs(curr_gy - start_gy)

            target_gx, target_gy = curr_gx, curr_gy

            if dx > dy:
                target_gy = start_gy
            else:
                target_gx = start_gx

            x1 = start_gx * self.level.TILE_SIZE + 16
            y1 = start_gy * self.level.TILE_SIZE + 16

            x2 = target_gx * self.level.TILE_SIZE + 16
            y2 = target_gy * self.level.TILE_SIZE + 16
            self.axis_drag_end_pos = (x2, y2)
            Debug.addDebugLine(x1, y1, x2, y2)

        self.end_frame()


if __name__ == "__main__":
    game = Game()
    game.run()