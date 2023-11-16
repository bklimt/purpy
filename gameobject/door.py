
import pygame

from enum import Enum, IntEnum

from constants import *
from imagemanager import ImageManager
from render.rendercontext import RenderContext
from render.spritebatch import SpriteBatch
from spritesheet import SpriteSheet
from tilemap import MapObject
from utils import intersect


class DoorLayer(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
    LOCKED = 2
    DOORS = 3
    FRAME = 4


class DoorState(Enum):
    LOCKED = 1
    UNLOCKING = 2
    OPEN = 3
    CLOSING = 4
    CLOSED = 5


class Door:
    x: int
    y: int
    sprite: SpriteSheet
    destination: str | None
    stars_needed: int
    stars_remaining: int
    active: bool

    state: DoorState
    frame: int = 0

    def __init__(self, obj: MapObject):
        surface = pygame.image.load('assets/sprites/door.png')
        self.sprite = SpriteSheet(surface, 32, 32)
        self.x = obj.x * SUBPIXELS
        self.y = obj.y * SUBPIXELS
        self.active = False

        dest = obj.properties.get('destination', None)
        if dest is not None and not isinstance(dest, str):
            raise Exception('door destination must be a string')
        self.destination = dest

        stars_needed = obj.properties.get('stars_needed', 0)
        if not isinstance(stars_needed, int):
            raise Exception(f'stars_needed was not an int: {stars_needed}')
        self.stars_needed = stars_needed
        self.stars_remaining = stars_needed

        self.state = DoorState.LOCKED if self.stars_needed > 0 else DoorState.OPEN

    def draw_background(self, context: RenderContext, batch: SpriteBatch, offset: tuple[int, int], images: ImageManager):
        pos = (self.x + offset[0], self.y + offset[1])
        dest = pygame.Rect(pos[0], pos[1], 32 *
                           context.subpixels, 32 * context.subpixels)
        layer = DoorLayer.ACTIVE if self.active else DoorLayer.INACTIVE
        self.sprite.blit(batch, dest, 0, layer=layer)
        if self.state == DoorState.LOCKED:
            self.sprite.blit(batch,
                             dest,
                             index=0,
                             layer=DoorLayer.LOCKED)
        if self.state == DoorState.UNLOCKING:
            self.sprite.blit(batch,
                             dest,
                             index=(self.frame // DOOR_SPEED),
                             layer=DoorLayer.LOCKED)
        if self.stars_remaining > 0:
            s = str(self.stars_remaining)
            if len(s) == 1:
                s = '0' + s
            images.font.draw_string(batch,
                                    (pos[0] + 8*context.subpixels,
                                     pos[1] + 12*context.subpixels),
                                    s)

    def draw_foreground(self, context: RenderContext, batch: SpriteBatch, offset: tuple[int, int]):
        pos = (self.x + offset[0], self.y + offset[1])
        dest = pygame.Rect(pos[0], pos[1], 32 *
                           context.subpixels, 32 * context.subpixels)
        if self.state == DoorState.CLOSING:
            self.sprite.blit(batch,
                             dest,
                             index=(self.frame // DOOR_SPEED),
                             layer=DoorLayer.DOORS)
        if self.state == DoorState.CLOSED:
            self.sprite.blit(batch,
                             dest,
                             index=DOOR_CLOSING_FRAMES - 1,
                             layer=DoorLayer.DOORS)
        self.sprite.blit(batch, dest, layer=DoorLayer.FRAME)

    def is_inside(self, player_rect: pygame.Rect) -> bool:
        door_rect = pygame.Rect(self.x + 8*SUBPIXELS,
                                self.y,
                                24*SUBPIXELS,
                                32*SUBPIXELS)
        return intersect(player_rect, door_rect)

    def update(self, player_rect: pygame.Rect, star_count: int):
        self.active = self.is_inside(player_rect)
        self.stars_remaining = max(0, self.stars_needed - star_count)

        if self.state == DoorState.UNLOCKING:
            max_frame = DOOR_UNLOCKING_FRAMES * DOOR_SPEED
            if self.frame == max_frame:
                self.state = DoorState.OPEN
            self.frame = min(self.frame + 1, max_frame)

        if self.state == DoorState.CLOSING:
            max_frame = DOOR_CLOSING_FRAMES * DOOR_SPEED
            if self.frame == max_frame:
                self.state = DoorState.CLOSED
            self.frame = min(self.frame + 1, max_frame)

        if self.state == DoorState.LOCKED:
            if star_count >= self.stars_needed:
                self.unlock()

    @property
    def is_open(self) -> bool:
        return self.state == DoorState.OPEN

    @property
    def is_closed(self) -> bool:
        return self.state == DoorState.CLOSED

    def unlock(self):
        if self.state != DoorState.LOCKED:
            return
        self.state = DoorState.UNLOCKING
        self.frame = 0

    def close(self):
        if self.state != DoorState.OPEN:
            return
        self.state = DoorState.CLOSING
        self.frame = 0
