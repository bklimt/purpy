
import pygame
import typing

from player import Player
from tilemap import MapObject
from tileset import TileSet
from random import randint
from soundmanager import SoundManager
from spritesheet import SpriteSheet
from switchstate import SwitchState
from utils import assert_int, assert_str, try_move_to_bounds, Bounds, Direction

BAGEL_WAIT_TIME = 30
BAGEL_FALL_TIME = 150
BAGEL_MAX_GRAVITY = 11
BAGEL_GRAVITY_ACCELERATION = 1


def sign(n: int) -> int:
    if n == 0:
        return 0
    if n < 0:
        return -1
    if n > 0:
        return 1
    raise Exception('impossible')


class Platform(typing.Protocol):
    id: int
    dx: int
    dy: int
    is_solid: bool
    occupied: bool

    def update(self, switches: SwitchState, sounds: SoundManager) -> None:
        raise Exception('abstract protocol')

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]) -> None:
        raise Exception('abstract protocol')

    def try_move_to(self, player_rect: Bounds, direction: Direction, is_backwards: bool) -> int:
        raise Exception('abstract protocol')


class PlatformBase:
    id: int
    tileset: TileSet
    tile_id: int
    x: int
    y: int
    dx: int
    dy: int
    occupied: bool
    is_solid: bool

    def __init__(self, obj: MapObject, tileset: TileSet):
        if obj.gid is None:
            raise Exception('platforms must have tile ids')

        self.id = obj.id
        self.tileset = tileset
        self.tile_id = obj.gid - 1
        self.x = obj.x * 16
        self.y = obj.y * 16
        self.dx = 0
        self.dy = 0
        self.occupied = False
        self.is_solid = bool(obj.properties.get('solid', False))

        pass

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]):
        x = self.x//16 + offset[0]
        y = self.y//16 + offset[1]
        if self.tile_id in self.tileset.animations:
            anim = self.tileset.animations[self.tile_id]
            anim.blit(surface, (x, y), False)
        else:
            area = self.tileset.get_source_rect(self.tile_id)
            surface.blit(self.tileset.surface, (x, y), area)

    def try_move_to(self, player_rect: Bounds, direction: Direction, is_backwards: bool) -> int:
        if self.is_solid:
            area = Bounds(
                self.x,
                self.y,
                self.tileset.tilewidth * 16,
                self.tileset.tileheight * 16)
            return try_move_to_bounds(player_rect, area, direction)
        else:
            if direction != Direction.DOWN:
                return 0
            if is_backwards:
                return 0
            area = Bounds(
                self.x,
                self.y,
                self.tileset.tilewidth * 16,
                4 * 16)
            return try_move_to_bounds(player_rect, area, direction)


class MovingPlatform(PlatformBase):
    distance: int
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    moving_forward: bool
    condition: str | None
    overflow: str

    def __init__(self, obj: MapObject, tileset: TileSet):
        super().__init__(obj, tileset)
        self.distance = assert_int(obj.properties.get('distance', '0')) * 16
        self.speed = assert_int(obj.properties.get('speed', '1'))
        self.start_x = self.x
        self.start_y = self.y
        self.moving_forward = True
        cond = obj.properties.get('condition')
        self.condition = assert_str(cond) if cond is not None else None
        self.overflow = assert_str(obj.properties.get('overflow', 'oscillate'))
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

        self.dx = 0
        self.dy = 0

    def update(self, switches: SwitchState, sounds: SoundManager):
        if self.condition != None:
            if not switches.is_condition_true(self.condition):
                self.moving_forward = False
                if self.x == self.start_x and self.y == self.start_y:
                    self.dx = 0
                    self.dy = 0
                    return

        self.dx = sign(self.end_x - self.start_x) * self.speed
        self.dy = sign(self.end_y - self.start_y) * self.speed
        if self.moving_forward:
            if self.x == self.end_x and self.y == self.end_y:
                if self.overflow == 'wrap':
                    self.x = self.start_x
                    self.y = self.start_y
                elif self.overflow == 'clamp':
                    self.dx = 0
                    self.dy = 0
                else:
                    self.dx *= -1
                    self.dy *= -1
                    self.moving_forward = False
        else:
            if self.x == self.start_x and self.y == self.start_y:
                self.moving_forward = True
            else:
                self.dx *= -1
                self.dy *= -1
        self.x += self.dx
        self.y += self.dy


class Bagel(PlatformBase):
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

    def update(self, switches: SwitchState, sounds: SoundManager):
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


class Conveyor(PlatformBase):
    def __init__(self, obj: MapObject, tileset: TileSet):
        super().__init__(obj, tileset)
        speed = int(obj.properties.get('speed', 24))
        if obj.properties.get('convey', 'E') == 'E':
            self.dx = speed
        else:
            self.dx = -1 * speed

    def update(self, switches: SwitchState, sounds: SoundManager):
        pass


SPRING_FRAMES = 4
STALL_FRAMES = 10


class Spring(PlatformBase):
    sprite: SpriteSheet
    up: bool = False
    position: int = 0
    stall_counter = STALL_FRAMES

    def __init__(self, obj: MapObject, tileset: TileSet):
        super().__init__(obj, tileset)
        surface = pygame.image.load('assets/sprites/spring.png')
        self.sprite = SpriteSheet(surface, 8, 8)

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]):
        x = self.x//16 + offset[0]
        y = self.y//16 + offset[1]
        self.sprite.blit(surface, (x, y), self.position)

    def should_boost(self):
        return self.up or (self.position == SPRING_FRAMES - 1)

    def update(self, switches: SwitchState, sounds: SoundManager):
        self.dx = 0
        self.dy = 0
        self.launch = False
        if not self.occupied:
            self.stall_counter = STALL_FRAMES
            self.up = False
            if self.position > 0:
                self.position -= 1
                self.dy = -1
        else:
            if self.up:
                self.stall_counter = STALL_FRAMES
                if self.position > 0:
                    self.position -= 1
                    self.dy = -1
                else:
                    self.launch = True
            else:
                if self.position < SPRING_FRAMES - 1:
                    self.stall_counter = STALL_FRAMES
                    self.position += 1
                    self.dy = 1
                else:
                    if self.stall_counter > 0:
                        self.stall_counter -= 1
                    else:
                        self.stall_counter = STALL_FRAMES
                        self.up = True
