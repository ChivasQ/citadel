import pygame
from pygame import RESIZABLE
from pygame.locals import DOUBLEBUF, OPENGL
import imgui
from imgui.integrations.pygame import PygameRenderer
from OpenGL.GL import *

from Debug import debug_text
from Debug import render
from Level import Level
from ResourceManager import ResourceManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800,500), RESIZABLE)
        self.resource_manager = ResourceManager()
        self.level = Level(self.screen, self.resource_manager)

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
                    if event.button == 1:  # 1 - left button
                        self.level.place_building()
                    if event.button == pygame.BUTTON_RIGHT:
                        self.level.destroy_building()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: self.level.build_mode = 0  # Wall
                    if event.key == pygame.K_2: self.level.build_mode = 1  # Miner
                    if event.key == pygame.K_3: self.level.build_mode = 2  # Conveyor
                    if event.key == pygame.K_4: self.level.build_mode = 3  # Furnace

                    if event.key == pygame.K_r:  # Rotate
                        self.level.rotate_building()

            self.update(dt)
            dt = self.clock.tick(0) / 1000






    def start_frame(self):
        self.screen.fill("blue")

    def end_frame(self):
        pygame.display.update()

    def update(self, dt):
        self.start_frame()

        self.level.update(dt)
        debug_text(f'FPS: {round(self.clock.get_fps(), 1)} DT: {dt}')
        render()

        self.end_frame()



if __name__ == "__main__":
    game = Game()
    game.run()