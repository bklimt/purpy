
import pygame

from spritesheet import SpriteSheet
from tilemap import MapObject

DOOR_SPEED = 3


class Door:
    x: int
    y: int
    sprite: SpriteSheet
    destination: str | None
    active: bool
    closing: bool = False
    frame: int = 0
    closed: bool = False

    def __init__(self, obj: MapObject):
        surface = pygame.image.load('assets/sprites/door.png')
        self.sprite = SpriteSheet(surface, 32, 32)
        self.x = obj.x
        self.y = obj.y
        self.active = False
        dest = obj.properties.get('destination', None)
        if dest is not None and not isinstance(dest, str):
            raise Exception('door destination must be a string')
        self.destination = dest

    def draw_background(self, surface: pygame.Surface, offset: tuple[int, int]):
        pos = (self.x + offset[0], self.y + offset[1])
        back_index = 0
        if self.active:
            back_index = 10
        self.sprite.blit(surface, pos, back_index, False)

    def draw_foreground(self, surface: pygame.Surface, offset: tuple[int, int]):
        pos = (self.x + offset[0], self.y + offset[1])
        self.sprite.blit(surface, pos, 20 + (self.frame // DOOR_SPEED), False)
        self.sprite.blit(surface, pos, 30, False)

    def is_inside(self, player_rect: pygame.Rect) -> bool:
        door_rect = pygame.Rect(self.x + 8, self.y + 8, 16, 24)
        if player_rect.left < door_rect.left:
            return False
        if player_rect.right > door_rect.right:
            return False
        if player_rect.top < door_rect.top:
            return False
        if player_rect.bottom > door_rect.bottom:
            return False
        return True

    def update(self, player_rect: pygame.Rect):
        self.active = self.is_inside(player_rect)
        if self.closing:
            max_frame = 9 * DOOR_SPEED
            if self.frame == max_frame:
                self.closed = True
            self.frame = min(self.frame + 1, max_frame)

    def close(self):
        self.closing = True
        self.frame = 0
