
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

    def __init__(self, obj: MapObject, tileset: TileSet, scale: int):
        self.area = pygame.Rect(
            obj.x*scale, obj.y*scale, obj.width*scale, obj.height*scale)
        self.surface = tileset.surface
        if not obj.gid:
            raise Exception('star must have gid')
        self.source = tileset.get_source_rect(obj.gid - 1)

    def intersects(self, player_rect: pygame.Rect):
        return intersect(self.area, player_rect)

    def draw(self, context: RenderContext, offset: tuple[int, int]):
        x = self.area.x + offset[0]
        y = self.area.y + offset[1]
        x += trunc(randint(-20, 20) / 20) * context.subpixels
        y += trunc(randint(-20, 20) / 20) * context.subpixels
        rect = pygame.Rect(x, y, self.area.w, self.area.h)
        context.player_batch.draw(self.surface, rect, self.source)
        # These constants were hand-tuned to make the stars look nice.
        context.add_light((x + 3 * context.subpixels,
                           y + 5 * context.subpixels),
                          12 * context.subpixels)
