
import pygame
import typing

from tilemap import MapObject
from tileset import TileSet
from random import randint
from soundmanager import SoundManager
from render.rendercontext import RenderContext
from render.spritebatch import SpriteBatch
from spritesheet import SpriteSheet
from switchstate import SwitchState
from utils import assert_int, assert_str, try_move_to_bounds, Direction

BAGEL_WAIT_TIME = 30
BAGEL_FALL_TIME = 150
BAGEL_MAX_GRAVITY = 11
BAGEL_GRAVITY_ACCELERATION = 1

SPRING_STEPS = 4
SPRING_STALL_FRAMES = 10
SPRING_SPEED = 16


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

    def draw(self, context: RenderContext, batch: SpriteBatch, offset: tuple[int, int]) -> None:
        raise Exception('abstract protocol')

    def try_move_to(self, player_rect: pygame.Rect, direction: Direction, is_backwards: bool) -> int:
        raise Exception('abstract protocol')


class PlatformBase:
    id: int
    tileset: TileSet
    tile_id: int
    x: int
    y: int
    width: int
    height: int
    dx: int
    dy: int
    occupied: bool
    is_solid: bool

    def __init__(self, obj: MapObject, tileset: TileSet, scale: int):
        if obj.gid is None:
            raise Exception('platforms must have tile ids')

        self.id = obj.id
        self.tileset = tileset
        self.tile_id = obj.gid - 1
        self.x = obj.x * scale
        self.y = obj.y * scale
        self.width = obj.width * scale
        self.height = obj.height * scale
        self.dx = 0
        self.dy = 0
        self.occupied = False
        self.is_solid = bool(obj.properties.get('solid', False))

        pass

    def draw(self, context: RenderContext, batch: SpriteBatch, offset: tuple[int, int]):
        x = self.x + offset[0]
        y = self.y + offset[1]
        dest = pygame.Rect(x, y, self.width, self.height)
        if self.tile_id in self.tileset.animations:
            anim = self.tileset.animations[self.tile_id]
            anim.blit(batch, dest, False)
        else:
            area = self.tileset.get_source_rect(self.tile_id)
            batch.draw(self.tileset.surface, dest, area)

    def try_move_to(self, player_rect: pygame.Rect, direction: Direction, is_backwards: bool) -> int:
        if self.is_solid:
            area = pygame.Rect(
                self.x,
                self.y,
                self.width,
                self.height)
            return try_move_to_bounds(player_rect, area, direction)
        else:
            if direction != Direction.DOWN:
                return 0
            if is_backwards:
                return 0
            area = pygame.Rect(
                self.x,
                self.y,
                self.width,
                self.height//2)
            return try_move_to_bounds(player_rect, area, direction)


class MovingPlatform(PlatformBase):
    direction: Direction
    distance: int
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    moving_forward: bool
    condition: str | None
    overflow: str

    def __init__(self, obj: MapObject, tileset: TileSet, scale: int):
        super().__init__(obj, tileset, scale)
        self.distance = assert_int(obj.properties.get('distance', '0')) * scale
        self.speed = assert_int(obj.properties.get('speed', '1'))
        self.start_x = self.x
        self.start_y = self.y
        self.moving_forward = True
        cond = obj.properties.get('condition')
        self.condition = assert_str(cond) if cond is not None else None
        self.overflow = assert_str(obj.properties.get('overflow', 'oscillate'))
        d = str(obj.properties.get('direction', 'N')).upper()
        if d == 'N':
            self.direction = Direction.UP
            self.distance *= self.tileset.tileheight
            self.end_x = self.start_x
            self.end_y = self.start_y - self.distance
        elif d == 'S':
            self.direction = Direction.DOWN
            self.distance *= self.tileset.tileheight
            self.end_x = self.start_x
            self.end_y = self.start_y + self.distance
        elif d == 'E':
            self.direction = Direction.RIGHT
            self.distance *= self.tileset.tilewidth
            self.end_x = self.start_x + self.distance
            self.end_y = self.start_y
        elif d == 'W':
            self.direction = Direction.LEFT
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
            if self.direction == Direction.UP:
                if self.y <= self.end_y:
                    if self.overflow == 'wrap':
                        self.y += self.distance
                    elif self.overflow == 'clamp':
                        self.dy = 0
                        self.y = self.end_y + 1
                    else:
                        self.dy *= -1
                        self.moving_forward = False
            elif self.direction == Direction.DOWN:
                if self.y >= self.end_y:
                    if self.overflow == 'wrap':
                        self.y = self.start_y + (self.end_y - self.y)
                    elif self.overflow == 'clamp':
                        self.dy = 0
                        self.y = self.end_y - 1
                    else:
                        self.dy *= -1
                        self.moving_forward = False
            if self.direction == Direction.LEFT:
                if self.x <= self.end_x:
                    if self.overflow == 'wrap':
                        self.x += self.distance
                    elif self.overflow == 'clamp':
                        self.dx = 0
                        self.x = self.end_x + 1
                    else:
                        self.dx *= -1
                        self.moving_forward = False
            elif self.direction == Direction.RIGHT:
                if self.x >= self.end_x:
                    if self.overflow == 'wrap':
                        self.x = self.start_x + (self.end_x - self.x)
                    elif self.overflow == 'clamp':
                        self.dx = 0
                        self.x = self.end_x - 1
                    else:
                        self.dx *= -1
                        self.moving_forward = False
        else:
            # If must be oscillating.
            if self.direction == Direction.UP and self.y >= self.start_y:
                self.moving_forward = True
            elif self.direction == Direction.DOWN and self.y <= self.start_y:
                self.moving_forward = True
            elif self.direction == Direction.LEFT and self.x >= self.start_x:
                self.moving_forward = True
            elif self.direction == Direction.RIGHT and self.x <= self.start_x:
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

    def __init__(self, obj: MapObject, tileset: TileSet, scale: int):
        super().__init__(obj, tileset, scale)
        self.original_y = self.y

    def draw(self, context: RenderContext, batch: SpriteBatch, offset: tuple[int, int]):
        x = self.x + offset[0]
        y = self.y + offset[1]
        area = self.tileset.get_source_rect(self.tile_id)
        if self.occupied:
            x += randint(-1, 1)
            y += randint(-1, 1)
        # TODO: Change this.
        rect = pygame.Rect(x, y, area.w * 16, area.h * 16)
        batch.draw(self.tileset.surface, rect, area)

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
    def __init__(self, obj: MapObject, tileset: TileSet, scale: int):
        super().__init__(obj, tileset, scale)
        speed = int(obj.properties.get('speed', 24))
        if obj.properties.get('convey', 'E') == 'E':
            self.dx = speed
        else:
            self.dx = -1 * speed

    def update(self, switches: SwitchState, sounds: SoundManager):
        pass


class Spring(PlatformBase):
    sprite: SpriteSheet
    up: bool = False
    position: int = 0
    stall_counter = SPRING_STALL_FRAMES
    scale: int

    def __init__(self, obj: MapObject, tileset: TileSet, scale: int):
        super().__init__(obj, tileset, scale)
        surface = pygame.image.load('assets/sprites/spring.png')
        self.sprite = SpriteSheet(surface, 8, 8)
        self.scale = scale

    @property
    def frame(self):
        return self.position // self.scale

    def draw(self, context: RenderContext, batch: SpriteBatch, offset: tuple[int, int]):
        x = self.x + offset[0]
        y = self.y + offset[1]
        dest = pygame.Rect(x, y, self.width, self.height)
        self.sprite.blit(batch, dest, self.frame)

    def should_boost(self):
        return self.up or (self.frame == SPRING_STEPS - 1)

    def update(self, switches: SwitchState, sounds: SoundManager):
        self.dx = 0
        self.dy = 0
        self.launch = False
        if not self.occupied:
            self.stall_counter = SPRING_STALL_FRAMES
            self.up = False
            if self.position > 0:
                self.position -= SPRING_SPEED
                self.dy = -SPRING_SPEED
        else:
            if self.up:
                self.stall_counter = SPRING_STALL_FRAMES
                if self.position > 0:
                    self.position -= SPRING_SPEED
                    self.dy = -SPRING_SPEED
                else:
                    self.launch = True
            else:
                if self.position < (SPRING_STEPS * self.scale) - SPRING_SPEED:
                    self.stall_counter = SPRING_STALL_FRAMES
                    self.position += SPRING_SPEED
                    self.dy = SPRING_SPEED
                else:
                    if self.stall_counter > 0:
                        self.stall_counter -= 1
                    else:
                        self.stall_counter = SPRING_STALL_FRAMES
                        self.up = True

    def try_move_to(self, player_rect: pygame.Rect, direction: Direction, is_backwards: bool) -> int:
        if self.is_solid:
            area = pygame.Rect(
                self.x,
                self.y + self.position,
                self.width,
                self.height - self.position)
            return try_move_to_bounds(player_rect, area, direction)
        else:
            if direction != Direction.DOWN:
                return 0
            if is_backwards:
                return 0
            area = pygame.Rect(
                self.x,
                self.y + self.position,
                self.width,
                self.height//2)
            return try_move_to_bounds(player_rect, area, direction)
