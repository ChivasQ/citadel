import pygame
pygame.init()
font = pygame.font.Font("resources/fonts/PressStart2P-Regular.ttf", 20)

text = []
lines = []

def debug_text(info, x = 10, y = 10):
    text.append((info, x, y))

def renderDebugText():
    display_surface = pygame.display.get_surface()
    for i in text:
        info, x, y = i
        text_surface = font.render(str(info), False, "White")
        display_surface.blit(text_surface, (x, y))
    text.clear()

def renderLines(camera_offset):

    global lines
    remaining_lines = []
    display_surface = pygame.display.get_surface()
    color = (255, 50, 50)
    width = 2
    for line_data in lines:
        wx1, wy1, wx2, wy2, lifetime = line_data

        if lifetime > 0:
            sx1 = wx1 - camera_offset.x
            sy1 = wy1 - camera_offset.y
            sx2 = wx2 - camera_offset.x
            sy2 = wy2 - camera_offset.y

            pygame.draw.line(display_surface, color, (sx1, sy1), (sx2, sy2), width)

            remaining_lines.append((wx1, wy1, wx2, wy2, lifetime - 1))

    lines = remaining_lines


def addLine(x1, y1, x2, y2, lifetime = 1):
    lines.append((x1, y1, x2, y2, 1)) # 1 це життя ціеї лінії