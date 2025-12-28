from Building import Building
from Item import Item


class Miner(Building):
    def __init__(self, pos, grid_pos, groups, image, ore_type, level_ref):
        super().__init__(pos, grid_pos, groups, image)
        self.ore_type = ore_type
        self.level = level_ref  # Посилання на рівень для доступу до сусідів

        self.mining_speed = 1.0  # 1 предмет в секунду
        self.timer = 0

        # чи заблокований
        self.output_blocked = False

    def update(self, dt):
        # Якщо під буром немає руди, він не працює
        if not self.ore_type:
            return

        if not self.output_blocked:
            self.timer += dt

        # Коли час вийшов, пробуємо вивантажити ресурс
        if self.timer >= 1.0 / self.mining_speed:
            if self.try_output():
                self.timer = 0
                self.output_blocked = False
                print(f"Miner at {self.grid_pos} produced {self.ore_type}")
            else:
                # блокуємося і чекаємо звільнення місця
                self.output_blocked = True

    def try_output(self):
        tex = self.level.item_textures.get(self.ore_type)
        if not tex: return False

        new_item = Item(self.rect.center, self.ore_type, tex, [])

        DIR_VECS = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        for dx, dy in DIR_VECS:
            nx = self.grid_pos[0] + dx
            ny = self.grid_pos[1] + dy

            neighbor = self.level.world_data.get((nx, ny))

            if neighbor and hasattr(neighbor, 'accept_item'):
                # Якщо має атрибут direction, перевіряємо куди він дивиться
                if hasattr(neighbor, 'direction'):
                    # Отримуємо вектор, куди дивиться конвеєр
                    n_vec = DIR_VECS[neighbor.direction]
                    # Якщо вектор конвеєра не дивиться від будівлі
                    if n_vec != (dx, dy):
                        continue
                if neighbor.accept_item(new_item):
                    self.level.items_group.add(new_item)
                    return True

        return False

    def get_info(self):
        info = super().get_info()

        info.append(f"Target: {self.ore_type}")

        progress = int((self.timer * self.mining_speed) * 100)

        if self.output_blocked:
            info.append("Status: BLOCKED")
        else:
            info.append(f"Progress: {min(progress, 100)}%")

        return info