import pygame

from Building import Building

VECS = [pygame.math.Vector2(1, 0), pygame.math.Vector2(0, 1),
        pygame.math.Vector2(-1, 0), pygame.math.Vector2(0, -1)]

class Conveyor(Building):
    def __init__(self, pos, grid_pos, groups, image, direction, level_ref):
        super().__init__(pos, grid_pos, groups, image)
        self.direction = direction  # 0, 1, 2, 3
        self.level = level_ref

        # Посилання на предмет, який зараз на конвеєрі
        self.item = None
        self.speed = 60.0  # Пікселів на секунду

        # Повертаємо текстуру відповідно до напрямку
        # вправо
        angle = -90 * self.direction
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def accept_item(self, item):
        if self.item is None:
            self.item = item

            self.item.pos = pygame.math.Vector2(self.rect.center)
            return True
        return False

    def kill(self):
        # Якщо конвеєр тримає предмет, знищуємо і предмет теж
        if self.item:
            self.item.kill()
        super().kill()

    def update(self, dt):
        if self.item:
            # Цільова точка - центр наступного тайла
            target_vec = VECS[self.direction]
            # Але ми рухаємо тільки до центру поточного тайла + трохи вперед (на вихід)

            move_amount = target_vec * self.speed * dt
            self.item.pos += move_amount

            # Рахуємо відстань від центру тайла до предмета
            center = pygame.math.Vector2(self.rect.center)
            dist = (self.item.pos - center).length()

            # Якщо предмет віддалився від центру на 16 пікселів, спроба передати сусіду
            if dist >= 16:
                self.try_pass_to_neighbor()

    def try_pass_to_neighbor(self):
        dx, dy = list(VECS[self.direction])
        nx, ny = int(self.grid_pos[0] + dx), int(self.grid_pos[1] + dy)

        neighbor = self.level.world_data.get((nx, ny))

        # Якщо там є конвеєр, або інша споруда з accept_item методом
        if neighbor and hasattr(neighbor, 'accept_item'):
            if neighbor.accept_item(self.item):
                # Успішна передача
                self.item = None
            else:
                self.item.pos -= VECS[self.direction] * 2
        else:
            self.item.pos -= VECS[self.direction] * 2