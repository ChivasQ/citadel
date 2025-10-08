import pygame
from pygame.locals import DOUBLEBUF, OPENGL
import imgui
from imgui.integrations.pygame import PygameRenderer
from OpenGL.GL import *

from Debug import debug_text
from Level import Level


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800,500))
        self.level = Level(self.screen)
        pygame.display.set_caption("game")
        self.clock = pygame.time.Clock()

    def run(self):
        isRunning = True
        while isRunning:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    isRunning = False
                    # onExit()
                    return

            self.update()

    def start_frame(self):
        self.screen.fill("blue")

    def end_frame(self):
        pygame.display.update()
        self.clock.tick(0)

    def update(self):
        self.start_frame()

        self.level.update()
        debug_text(f'FPS: {round(self.clock.get_fps(), 1)}')


        self.end_frame()



if __name__ == "__main__":
    game = Game()
    game.run()