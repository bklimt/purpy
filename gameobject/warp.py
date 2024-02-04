
import pygame

from constants import SUBPIXELS
from tilemap import MapObject
from utils import intersect


class Warp:
    position: pygame.Rect
    destination: str

    def __init__(self, obj: MapObject):
        if obj.properties.warp is None:
            raise Exception("invalid warp destination")

        rect = obj.rect().copy()
        rect.x *= SUBPIXELS
        rect.y *= SUBPIXELS
        rect.w *= SUBPIXELS
        rect.h *= SUBPIXELS

        self.position = rect
        self.destination = obj.properties.warp

    def is_inside(self, player_rect: pygame.Rect) -> bool:
        return intersect(player_rect, self.position)
