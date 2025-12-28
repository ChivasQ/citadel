from Building import Building


class Core(Building):
    def __init__(self, pos, grid_pos, groups, image, level_ref):
        # pos - це координати верхнього лівого кута
        super().__init__(pos, grid_pos, groups, image)
        self.level = level_ref
        self.health = 2000
        self.max_health = 2000
        self.size = 3  # Розмір 3x3 клітинки

        # Переконаємося, що rect починається з переданої позиції
        self.rect = self.image.get_rect(topleft=pos)

    def accept_item(self, item):
        item_type = item.item_type
        if item_type in self.level.inventory:
            self.level.inventory[item_type] += 1
        else:
            self.level.inventory[item_type] = 1

        item.kill()
        return True

    def get_info(self):
        info = super().get_info()
        info.append("--- CORE STORAGE ---")
        for res, count in self.level.inventory.items():
            info.append(f"{res.capitalize()}: {count}")
        return info