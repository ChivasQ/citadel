from Building import Building
from Item import Item


class Furnace(Building):
    def __init__(self, pos, grid_pos, groups, image, level_ref):
        super().__init__(pos, grid_pos, groups, image)
        self.level = level_ref

        self.inventory = {'coal': 0, 'copper': 0}
        self.max_capacity = 10

        self.output_item_type = None

        self.timer = 0
        self.process_time = 2.0

    def accept_item(self, item):
        if self.output_item_type is not None:
            return False

        item_type = item.item_type

        if item_type in self.inventory:
            if self.inventory[item_type] < self.max_capacity:
                self.inventory[item_type] += 1
                print(f"Furnace received {item_type}. Stored: {self.inventory}")
                item.kill()  # Видаляємо фізичний предмет, він перейшов в інвентар
                return True

        return False

    def update(self, dt):
        if self.output_item_type:
            if self.try_output():
                self.output_item_type = None  # Очистили вихід

        # 1 вугілля + 1 мідь = 1 мідний злиток
        elif self.inventory['coal'] >= 1 and self.inventory['copper'] >= 1:
            self.timer += dt
            if self.timer >= self.process_time:
                self.craft()
                self.timer = 0

    def craft(self):

        self.inventory['coal'] -= 1
        self.inventory['copper'] -= 1

        self.output_item_type = 'copper_ingot'
        print("Crafted Copper Ingot!")

    def try_output(self):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        DIR_VECS_MAP = {
            (1, 0): 0,  # Right
            (0, 1): 1,  # Down
            (-1, 0): 2,  # Left
            (0, -1): 3  # Up
        }

        tex = self.level.item_textures.get(self.output_item_type)

        temp_item = Item(self.rect.center, self.output_item_type, tex, [])

        for dx, dy in directions:
            nx, ny = self.grid_pos[0] + dx, self.grid_pos[1] + dy
            neighbor = self.level.world_data.get((nx, ny))
            if neighbor and hasattr(neighbor, 'accept_item'):
                if hasattr(neighbor, 'direction'):
                    required_dir = DIR_VECS_MAP.get((dx, dy))
                    if neighbor.direction != required_dir:
                        continue

                if neighbor.accept_item(temp_item):
                    self.level.items_group.add(temp_item)
                    return True

        temp_item.kill()
        return False

    def get_info(self):
        info = super().get_info()

        info.append("--- Inventory ---")
        for res, count in self.inventory.items():
            info.append(f"{res.capitalize()}: {count}/{self.max_capacity}")

        if self.output_item_type:
            info.append(f"Output: {self.output_item_type} (BLOCKED)")
        else:
            # Прогрес плавки
            if self.timer > 0:
                progress = int((self.timer / self.process_time) * 100)
                info.append(f"Smelting: {progress}%")
            else:
                info.append("Status: Idle")

        return info