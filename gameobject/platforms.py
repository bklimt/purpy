
import pygame
import typing

from constants import *
from imagemanager import ImageManager
from properties import get_int, get_str
from tilemap import MapObject, TileMap
from random import randint
from soundmanager import SoundManager
from render.rendercontext import RenderContext
from render.spritebatch import SpriteBatch
from spritesheet import SpriteSheet
from switchstate import SwitchState
from utils import try_move_to_bounds, Direction


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
    tilemap: TileMap
    tile_id: int
    x: int
    y: int
    width: int
    height: int
    dx: int
    dy: int
    occupied: bool
    is_solid: bool

    def __init__(self, obj: MapObject, tilemap: TileMap):
        if obj.gid is None:
            raise Exception('platforms must have tile ids')

        self.id = obj.id
        self.tilemap = tilemap
        self.tile_id = obj.gid
        self.x = obj.x * SUBPIXELS
        self.y = obj.y * SUBPIXELS
        self.width = obj.width * SUBPIXELS
        self.height = obj.height * SUBPIXELS
        self.dx = 0
        self.dy = 0
        self.occupied = False
        self.is_solid = bool(obj.properties.get('solid', False))

    def draw(self, context: RenderContext, batch: SpriteBatch, offset: tuple[int, int]):
        x = self.x + offset[0]
        y = self.y + offset[1]
        dest = pygame.Rect(x, y, self.width, self.height)
        anim = self.tilemap.get_animation(self.tile_id)
        if anim is not None:
            anim.blit(batch, dest, False)
        else:
            self.tilemap.draw_tile(batch, self.tile_id, dest)

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

    def __init__(self, obj: MapObject, tilemap: TileMap):
        super().__init__(obj, tilemap)
        self.distance = get_int(obj.properties, 'distance', 0) * SUBPIXELS
        # This is 16 for historical reasons, just because that's what the speed is tuned for.
        self.speed = (get_int(obj.properties, 'speed', 1) * SUBPIXELS) // 16
        self.start_x = self.x
        self.start_y = self.y
        self.moving_forward = True
        self.condition = get_str(obj.properties, 'condition')
        self.overflow = get_str(obj.properties, 'overflow', 'oscillate')
        d = get_str(obj.properties, 'direction', 'N').upper()
        if d == 'N':
            self.direction = Direction.UP
            self.distance *= self.tilemap.tileheight
            self.end_x = self.start_x
            self.end_y = self.start_y - self.distance
        elif d == 'S':
            self.direction = Direction.DOWN
            self.distance *= self.tilemap.tileheight
            self.end_x = self.start_x
            self.end_y = self.start_y + self.distance
        elif d == 'E':
            self.direction = Direction.RIGHT
            self.distance *= self.tilemap.tilewidth
            self.end_x = self.start_x + self.distance
            self.end_y = self.start_y
        elif d == 'W':
            self.direction = Direction.LEFT
            self.distance *= self.tilemap.tilewidth
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

    def __init__(self, obj: MapObject, tilemap: TileMap):
        super().__init__(obj, tilemap)
        self.original_y = self.y

    def draw(self, context: RenderContext, batch: SpriteBatch, offset: tuple[int, int]):
        x = self.x + offset[0]
        y = self.y + offset[1]
        if self.occupied:
            x += randint(-1, 1)
            y += randint(-1, 1)
        rect = pygame.Rect(x, y, self.tilemap.tilewidth *
                           SUBPIXELS, self.tilemap.height * SUBPIXELS)
        if rect.bottom < 0 or rect.right < 0:
            return
        if rect.top >= context.logical_area.h or rect.right >= context.logical_area.w:
            return
        self.tilemap.draw_tile(batch, self.tile_id, rect)

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
    def __init__(self, obj: MapObject, tilemap: TileMap):
        super().__init__(obj, tilemap)
        # This is hand-tuned.
        speed = int(obj.properties.get('speed', 24)) * SUBPIXELS//16
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

    def __init__(self, obj: MapObject, tilemap: TileMap, images: ImageManager):
        super().__init__(obj, tilemap)
        surface = images.load_image('assets/sprites/spring.png')
        self.sprite = SpriteSheet(surface, 8, 8)

    @property
    def frame(self):
        return self.position // SUBPIXELS

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
                if self.position < (SPRING_STEPS * SUBPIXELS) - SPRING_SPEED:
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
