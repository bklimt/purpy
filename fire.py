
import pygame
from random import randint
from tilemap import MapObject


def hue_to_rgb(p: float, q: float, t: float):
    if t < 0.0:
        t += 1
    if t > 1.0:
        t -= 1
    if t < 1.0 / 6.0:
        return p + (q - p) * 6.0 * t
    if t < 1.0 / 2.0:
        return q
    if t < 2.0 / 3.0:
        return p + (q - p) * (2.0 / 3.0 - t) * 6
    return p


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    r = int(hue_to_rgb(p, q, h + 1.0 / 3.0) * 255.0)
    g = int(hue_to_rgb(p, q, h) * 255.0)
    b = int(hue_to_rgb(p, q, h - 1.0 / 3.0) * 255.0)
    return (r, g, b)


class Fire:
    x: int
    y: int
    width: int
    height: int
    surface: pygame.Surface
    palette: list[pygame.Color]
    fire: list[list[int]]
    burning: list[list[float]]

    def __init__(self, obj: MapObject):
        self.x = obj.x
        self.y = obj.y
        self.width = obj.width
        self.height = obj.height
        self.surface = pygame.Surface(
            (self.width, self.height), pygame.SRCALPHA)

        # Initialize the palette.
        self.palette = []
        for i in range(256):
            h = i / (3.0 * 256.0)
            s = 1.0
            l = min(255, i * 2) / 255.0

            r, g, b = hsl_to_rgb(h, s, l)

            alpha = ((i * 255) // 40) if i < 40 else 255
            self.palette.append(pygame.Color(r, g, b, alpha))

        self.fire = []
        self.burning = []
        for _ in range(self.height):
            self.fire.append([0] * self.width)
            self.burning.append([0.0] * self.width)

    def update(self, elapsed_ms):
        for y in range(self.height):
            for x in range(self.width):
                if True:
                    if y == self.height - 1:
                        self.fire[y][x] = randint(0, 255)
                else:
                    if self.burning[y][x] > 0.0:
                        self.fire[y][x] = randint(0, 255)
                        self.burning[y][x] -= elapsed_ms
                        if self.burning[y][x] < 0:
                            self.burning[y][x] = 0.0

        for y in range(self.height - 1):
            for x in range(self.width):
                sum: int = 0
                sum += self.fire[y + 1][x]
                sum += self.fire[y + 1][(x + 1) % self.width]
                sum += self.fire[y + 1][(x - 1 + self.width) % self.width]
                sum += self.fire[(y + 2) % self.height][x]
                sum = (sum * 32) // 130
                if sum < 0 or sum > 255:
                    raise Exception(f'Invalid sum: {sum}')
                self.fire[y][x] = sum

        for x in range(self.width):
            self.fire[self.height - 1][x] //= 2

        for y in range(self.height):
            for x in range(self.width):
                color = self.palette[self.fire[y][x]]
                self.surface.set_at((x, y), color)

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]):
        surface.blit(self.surface, (self.x + offset[0], self.y + offset[1]))
