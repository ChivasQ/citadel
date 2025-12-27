import heapq
import math


class Pathfinding:
    @staticmethod
    def get_path(start, goal, world_data, map_width, map_height):
        neighbors = [(0, 1),
                     (0, -1),
                     (1, 0),
                     (-1, 0)]

        open_set = []
        heapq.heappush(open_set, (0, start))

        loops = 0
        max_loops = 1000

        came_from = {}
        g_score = {start: 0}
        f_score = {start: Pathfinding.heuristic(start, goal)}

        while open_set:
            loops += 1
            if loops > max_loops:
                return []

            current = heapq.heappop(open_set)[1]

            # Якщо дійшли до цілі
            if current == goal:
                return Pathfinding.reconstruct_path(came_from, current)

            for dx, dy in neighbors:
                neighbor = (current[0] + dx, current[1] + dy)

                # Перевірка перешкод
                # Ми вважаємо клітинку прохідною, якщо там немає будівлі,
                # АБО якщо ця будівля і є нашою ЦІЛЛЮ, щоб ми могли підійти до неї впритул
                if neighbor in world_data and neighbor != goal:
                    continue

                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f = tentative_g_score + Pathfinding.heuristic(neighbor, goal)
                    f_score[neighbor] = f
                    heapq.heappush(open_set, (f, neighbor))

        return []  # Шлях не знайдено

    @staticmethod
    def heuristic(a, b):
        # Манхеттенська відстань, а тепер Евкліда
        return math.dist(a, b)

    @staticmethod
    def reconstruct_path(came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        total_path.reverse()
        return total_path