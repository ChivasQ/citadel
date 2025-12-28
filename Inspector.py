import pygame


class Inspector:
    def __init__(self):
        self.font = pygame.font.Font("resources/fonts/PressStart2P-Regular.ttf", 14)
        self.bg_color = (0, 0, 0, 180)
        self.text_color = (255, 255, 255)
        self.padding = 10

    def draw(self, surface, mouse_pos, building):
        if not building:
            return

        lines = building.get_info()
        rendered_lines = []
        max_width = 0
        total_height = 0

        for line in lines:
            text_surf = self.font.render(line, True, self.text_color)
            rendered_lines.append(text_surf)

            if text_surf.get_width() > max_width:
                max_width = text_surf.get_width()
            total_height += text_surf.get_height() + 2

        box_width = max_width + self.padding * 2
        box_height = total_height + self.padding * 2

        x, y = mouse_pos
        x += 20
        y += 20

        screen_w, screen_h = surface.get_size()
        if x + box_width > screen_w:
            x -= box_width + 40
        if y + box_height > screen_h:
            y -= box_height + 40


        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surf, self.bg_color, (0, 0, box_width, box_height), 0)
        pygame.draw.rect(box_surf, "white", (0, 0, box_width, box_height), 1)

        surface.blit(box_surf, (x, y))

        current_y = y + self.padding
        for text_surf in rendered_lines:
            surface.blit(text_surf, (x + self.padding, current_y))
            current_y += text_surf.get_height() + 2