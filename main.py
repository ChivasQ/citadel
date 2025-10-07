import pygame
from pygame.locals import DOUBLEBUF, OPENGL
import imgui
from imgui.integrations.pygame import PygameRenderer
from OpenGL.GL import *


pygame.init()
screen = pygame.display.set_mode((800, 600)) # , DOUBLEBUF | OPENGL
pygame.display.set_caption("ImGui")
icon = pygame.image.load("resources/icon.png")
pygame.display.set_icon(icon)

font = pygame.font.Font("resources/fonts/PressStart2P-Regular.ttf", 40)
text_surface = font.render("text", False, "White")

imgui.create_context()
# impl = PygameRenderer()
# io = imgui.get_io()
# io.display_size = (800, 600)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # impl.process_event(event)
    #
    # imgui.new_frame()
    #
    # imgui.begin("Hello, ImGui!")
    # imgui.text("pygame :)")
    # if imgui.button("Press me"):
    #     print("Button pressed!")
    # imgui.end()
    screen.blit(text_surface, (100, 100))



    # glViewport(0, 0, 800, 600)
    # glClearColor(0.1, 0.1, 0.1, 1)
    # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # imgui.render()
    # impl.render(imgui.get_draw_data())

    pygame.display.flip()

# impl.shutdown()
pygame.quit()


