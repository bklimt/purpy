
import pygame

from random import randint
from tilemap import MapObject
from tileset import TileSet


from utils import intersect


class Star:
    area: pygame.Rect
    surface: pygame.Surface
    source: pygame.Rect

    def __init__(self, obj: MapObject, tileset: TileSet):
        self.area = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        self.surface = tileset.surface
        if not obj.gid:
            raise Exception('star must have gid')
        self.source = tileset.get_source_rect(obj.gid - 1)

    def intersects(self, player_rect: pygame.Rect):
        return intersect(self.area, player_rect)

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]):
        x = self.area.x + offset[0]
        y = self.area.y + offset[1]
        x += randint(-1, 1)
        y += randint(-1, 1)
        surface.blit(self.surface, (x, y), self.source)
