
import pygame

from math import trunc
from random import randint

from constants import SUBPIXELS
from render.rendercontext import RenderContext
from tilemap import MapObject, TileMap
from utils import intersect


class Star:
    area: pygame.Rect
    tilemap: TileMap
    tile_gid: int

    def __init__(self, obj: MapObject, tilemap: TileMap):
        self.area = pygame.Rect(
            obj.x*SUBPIXELS,
            obj.y*SUBPIXELS,
            obj.width*SUBPIXELS,
            obj.height*SUBPIXELS)
        if not obj.gid:
            raise Exception('star must have gid')
        self.tile_gid = obj.gid
        self.tilemap = tilemap

    def intersects(self, player_rect: pygame.Rect):
        return intersect(self.area, player_rect)

    def draw(self, context: RenderContext, offset: tuple[int, int]):
        x = self.area.x + offset[0]
        y = self.area.y + offset[1]
        x += trunc(randint(-20, 20) / 20) * SUBPIXELS
        y += trunc(randint(-20, 20) / 20) * SUBPIXELS
        rect = pygame.Rect(x, y, self.area.w, self.area.h)

        self.tilemap.draw_tile(context.player_batch, self.tile_gid, rect)
        # These constants were hand-tuned to make the stars look nice.
        context.add_light((x + 3 * SUBPIXELS,
                           y + 5 * SUBPIXELS),
                          12 * SUBPIXELS)
