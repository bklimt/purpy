
import pygame

from math import trunc
from random import randint

from render.rendercontext import RenderContext
from tilemap import MapObject
from tileset import TileSet
from utils import intersect


class Star:
    area: pygame.Rect
    surface: pygame.Surface
    source: pygame.Rect

    def __init__(self, obj: MapObject, tileset: TileSet):
        self.area = pygame.Rect(
            obj.x*16, obj.y*16, obj.width*16, obj.height*16)
        self.surface = tileset.surface
        if not obj.gid:
            raise Exception('star must have gid')
        self.source = tileset.get_source_rect(obj.gid - 1)

    def intersects(self, player_rect: pygame.Rect):
        return intersect(self.area, player_rect)

    def draw(self, context: RenderContext, offset: tuple[int, int]):
        x = (self.area.x + offset[0]) // 16
        y = (self.area.y + offset[1]) // 16
        x += trunc(randint(-20, 20) / 20)
        y += trunc(randint(-20, 20) / 20)
        context.player_surface.blit(self.surface, (x, y), self.source)
        context.add_light((x + 3, y + 5), 12)
