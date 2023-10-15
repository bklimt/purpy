
from enum import Enum
from tilemap import MapObject
from tileset import TileSet
import pygame


def sign(n: int) -> int:
    if n == 0:
        return 0
    if n < 0:
        return -1
    if n > 0:
        return 1
    raise Exception('impossible')


class Platform:
    tileset: TileSet
    tile_id: int
    distance: int
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    dx: int
    dy: int

    def __init__(self, obj: MapObject, tileset: TileSet):
        self.tileset = tileset
        self.tile_id = obj.gid
        self.distance = int(obj.properties.get('distance', '0')) * 16
        self.speed = int(obj.properties.get('speed', '1'))
        self.x = obj.x * 16
        self.y = obj.y * 16
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

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]):
        x = self.x//16 + offset[0]
        y = self.y//16 + offset[1]
        area = self.tileset.get_source_rect(self.tile_id)
        surface.blit(self.tileset.surface, (x, y), area)

    def intersect(self, rect: pygame.Rect):
        if rect.right < self.x//16:
            return False
        if rect.bottom < self.y//16:
            return False
        if rect.left > self.x//16 + self.tileset.tilewidth:
            return False
        if rect.top > self.y//16 + self.tileset.tileheight:
            return False
        return True
