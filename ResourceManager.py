import os

import pygame


class ResourceManager:
    def __init__(self):
        self.textures = {}

    def get_texture(self, path, size=None):
        # Ключ кешу включає шлях і розмір, щоб не масштабувати повторно, це доволі дорого d=====(￣▽￣*)b
        cache_key = (path, size)

        if cache_key in self.textures:
            return self.textures[cache_key]

        if not os.path.exists(path):
            print(f"Помилка: Файл {path} не знайдено.")
            # Повертаємо порожню поверхню, щоб гра не вилетіла
            fallback = pygame.Surface(size if size else (32, 32))
            fallback.fill((255, 0, 255))  # Рожевий колір
            return fallback

        try:
            image = pygame.image.load(path).convert_alpha()
            if size:
                image = pygame.transform.scale(image, size)

            self.textures[cache_key] = image
            return image
        except pygame.error as e:
            print(f"Не вдалося завантажити {path}: {e}")
            return None