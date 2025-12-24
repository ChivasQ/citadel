import pygame
from pygame import RESIZABLE
from pygame.locals import DOUBLEBUF, OPENGL
import imgui
from imgui.integrations.pygame import PygameRenderer
from OpenGL.GL import *

from Debug import debug_text
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
            self.update(dt)
            dt = self.clock.tick(0) / 1000 #divide by 1024, by bit shifting

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    isRunning = False
                    self.close()




    def start_frame(self):
        self.screen.fill("blue")

    def end_frame(self):
        pygame.display.update()

    def update(self, dt):
        self.start_frame()

        self.level.update(dt)
        debug_text(f'FPS: {round(self.clock.get_fps(), 1)} DT: {dt}')

        self.end_frame()



if __name__ == "__main__":
    game = Game()
    game.run()