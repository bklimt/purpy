
from enum import Enum
from tilemap import MapObject
from tileset import TileSet
from random import randint
import pygame

BAGEL_WAIT_TIME = 30
BAGEL_FALL_TIME = 150
BAGEL_MAX_GRAVITY = 24
BAGEL_GRAVITY_ACCELERATION = 1


def sign(n: int) -> int:
    if n == 0:
        return 0
    if n < 0:
        return -1
    if n > 0:
        return 1
    raise Exception('impossible')


class Platform:
    id: int
    tileset: TileSet
    tile_id: int
    x: int
    y: int
    dx: int
    dy: int
    occupied: bool

    def __init__(self, obj: MapObject, tileset: TileSet):
        self.id = obj.id
        self.tileset = tileset
        self.tile_id = obj.gid
        self.x = obj.x * 16
        self.y = obj.y * 16
        self.dx = 0
        self.dy = 0
        self.occupied = False

    def update(self):
        pass

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]):
        x = self.x//16 + offset[0]
        y = self.y//16 + offset[1]
        area = self.tileset.get_source_rect(self.tile_id)
        surface.blit(self.tileset.surface, (x, y), area)

    def intersect(self, rect: pygame.Rect) -> bool:
        if rect.right < self.x//16:
            return False
        if rect.bottom < self.y//16:
            return False
        if rect.left > self.x//16 + self.tileset.tilewidth:
            return False
        if rect.top > self.y//16 + self.tileset.tileheight:
            return False
        return True

    def intersect_top(self, rect: pygame.Rect) -> bool:
        if rect.right < self.x//16:
            return False
        if rect.left > self.x//16 + self.tileset.tilewidth:
            return False
        if rect.bottom != self.y//16:
            return False
        return True


class MovingPlatform(Platform):
    distance: int
    start_x: int
    start_y: int
    end_x: int
    end_y: int

    def __init__(self, obj: MapObject, tileset: TileSet):
        super().__init__(obj, tileset)
        self.distance = int(obj.properties.get('distance', '0')) * 16
        self.speed = int(obj.properties.get('speed', '1'))
        self.start_x = self.x
        self.start_y = self.y
        d = str(obj.properties.get('direction', 'N')).upper()
        if d == 'N':
            self.distance *= self.tileset.tileheight
            self.end_x = self.start_x
            self.end_y = self.start_y - self.distance
        elif d == 'S':
            self.distance *= self.tileset.tileheight
            self.end_x = self.start_x
            self.end_y = self.start_y + self.distance
        elif d == 'E':
            self.distance *= self.tileset.tilewidth
            self.end_x = self.start_x + self.distance
            self.end_y = self.start_y
        elif d == 'W':
            self.distance *= self.tileset.tilewidth
            self.end_x = self.start_x - self.distance
            self.end_y = self.start_y
        else:
            raise Exception(f'unknown direction {d}')

        self.dx = sign(self.end_x - self.start_x) * self.speed
        self.dy = sign(self.end_y - self.start_y) * self.speed

    def update(self):
        if self.x == self.end_x:
            self.dx *= -1
            self.start_x, self.end_x = self.end_x, self.start_x
        if self.y == self.end_y:
            self.dy *= -1
            self.start_y, self.end_y = self.end_y, self.start_y
        self.x += self.dx
        self.y += self.dy


class Bagel(Platform):
    original_y: int
    falling: bool = False
    remaining: int = BAGEL_WAIT_TIME

    def __init__(self, obj: MapObject, tileset: TileSet):
        super().__init__(obj, tileset)
        self.original_y = self.y

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]):
        x = self.x//16 + offset[0]
        y = self.y//16 + offset[1]
        area = self.tileset.get_source_rect(self.tile_id)
        if self.occupied:
            x += randint(-1, 1)
            y += randint(-1, 1)
        surface.blit(self.tileset.surface, (x, y), area)

    def update(self):
        if self.falling:
            self.remaining -= 1
            if self.remaining == 0:
                self.dy = 0
                self.y = self.original_y
                self.falling = False
                self.remaining = BAGEL_WAIT_TIME
            else:
                self.dy += BAGEL_GRAVITY_ACCELERATION
                self.dy = max(self.dy, BAGEL_MAX_GRAVITY)
                self.y += self.dy
        else:
            if self.occupied:
                self.remaining -= 1
                if self.remaining == 0:
                    self.falling = True
                    self.remaining = BAGEL_FALL_TIME
                    self.dy = 0
            else:
                self.remaining = BAGEL_WAIT_TIME
