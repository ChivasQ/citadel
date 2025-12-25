import pygame
from Building import Building
from Item import Item


class Miner(Building):
    def __init__(self, pos, grid_pos, groups, image, ore_type, level_ref):
        super().__init__(pos, grid_pos, groups, image)
        self.ore_type = ore_type
        self.level = level_ref  # Посилання на рівень для доступу до сусідів

        self.mining_speed = 1.0  # 1 предмет в секунду
        self.timer = 0

        # Прапорець, що показує, чи заблокований майнер (нікуди дівати руду)
        self.output_blocked = False

    def update(self, dt):
        # Якщо під буром немає руди, він не працює
        if not self.ore_type:
            return

        # Логіка таймера
        if not self.output_blocked:
            self.timer += dt

        # Коли час вийшов, пробуємо вивантажити ресурс
        if self.timer >= 1.0 / self.mining_speed:
            if self.try_output():
                # Якщо успішно вивантажили або створили предмет -> скидаємо таймер
                self.timer = 0
                self.output_blocked = False
                print(f"Miner at {self.grid_pos} produced {self.ore_type}")
            else:
                # Якщо нікуди діти -> блокуємося і чекаємо звільнення місця
                self.output_blocked = True

    def try_output(self):
        # Створюємо тимчасовий об'єкт предмета (віртуально)
        # Нам потрібен цей об'єкт, щоб передати його в accept_item конвеєра
        tex = self.level.item_textures.get(self.ore_type)
        if not tex: return False

        new_item = Item(self.rect.center, self.ore_type, tex, []) # без групи, щоб не відмальовувати

        # Пріоритет: Спроба передати сусідам
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dx, dy in directions:
            target_gx = self.grid_pos[0] + dx
            target_gy = self.grid_pos[1] + dy

            # Шукаємо будівлю-сусіда
            neighbor = self.level.world_data.get((target_gx, target_gy))

            # Якщо сусід існує і вміє приймати предмети (наприклад, Конвеєр)
            if neighbor and hasattr(neighbor, 'accept_item'):
                if neighbor.accept_item(new_item):
                    # Успішно передали! Тепер додаємо предмет у групу відображення
                    self.level.items_group.add(new_item)
                    return True

        return False