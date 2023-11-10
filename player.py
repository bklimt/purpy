
import pygame

from enum import Enum
from random import randint

from spritesheet import SpriteSheet
from utils import Bounds, Direction

FRAMES_PER_FRAME = 8
IDLE_TIME = 240


class PlayerState(Enum):
    FALLING = 1
    STANDING = 2
    CROUCHING = 3
    WALL_SLIDING = 4
    STOPPED = 5
    JUMPING = 6


class Player:
    # These are in 1/16 sub-pixels.
    x: int = 0
    y: int = 0
    dx: int = 0
    dy: int = 0
    facing_right: bool = True
    # 24x24 sprite sheet
    texture: pygame.Surface
    sprite: SpriteSheet
    state: PlayerState = PlayerState.STANDING
    frame: int = 0
    frames_to_next_frame: int = FRAMES_PER_FRAME
    idle_counter: int = IDLE_TIME
    is_idle: bool = False
    is_dead: bool = False

    def __init__(self):
        self.texture = pygame.image.load('assets/sprites/skelly.png')
        self.sprite = SpriteSheet(self.texture, 24, 24)

    def draw(self, surface: pygame.Surface, pos: tuple[int, int]):
        if self.dx < 0:
            self.facing_right = False
        if self.dx > 0:
            self.facing_right = True
        # IDLE, IDLE, IDLE, CROUCH, WAVE, JUMP, RUN, RUN, RUN, RUN
        index = 0
        if self.state == PlayerState.FALLING:
            index = 5
        elif self.state == PlayerState.JUMPING:
            index = 6
        elif self.state == PlayerState.WALL_SLIDING:
            index = 10
        elif self.dx != 0 and self.state == PlayerState.STANDING:
            if self.frame < 6 or self.frame > 9:
                self.frame = 6
                self.frames_to_next_frame = FRAMES_PER_FRAME
            else:
                self.frames_to_next_frame -= 1
                if self.frames_to_next_frame <= 0:
                    self.frames_to_next_frame = FRAMES_PER_FRAME
                    self.frame += 1
                    if self.frame > 9:
                        self.frame = 6
            index = self.frame
        elif self.state == PlayerState.STANDING or self.state == PlayerState.STOPPED:
            if self.idle_counter > 0:
                self.idle_counter -= 1
                index = 0
            else:
                self.is_idle = True
                if self.frame != 1 and self.frame != 2:
                    self.frame = 1
                    self.frames_to_next_frame = FRAMES_PER_FRAME
                else:
                    self.frames_to_next_frame -= 1
                    if self.frames_to_next_frame <= 0:
                        self.frames_to_next_frame = FRAMES_PER_FRAME
                        self.frame += 1
                        if self.frame > 2:
                            self.frame = 0
                            self.idle_counter = IDLE_TIME
                index = self.frame
        elif self.state == PlayerState.CROUCHING:
            index = 3

        if self.state != PlayerState.STANDING or self.dx != 0:
            self.is_idle = False
            self.idle_counter = IDLE_TIME

        if self.is_dead:
            pos = (pos[0] + randint(-1, 1), pos[1] + randint(-1, 1))
        self.sprite.blit(surface,
                         pos,
                         index=index,
                         reverse=not self.facing_right)

        pos_sub = (pos[0]*16, pos[1]*16)

        if False:
            left = self.get_target_bounds_at(pos_sub, Direction.LEFT)
            surface.fill(pygame.Color(255, 0, 255, 63), left.rect)
            right = self.get_target_bounds_at(pos_sub, Direction.RIGHT)
            surface.fill(pygame.Color(127, 127, 63, 63), right.rect)
            up = self.get_target_bounds_at(pos_sub, Direction.UP)
            surface.fill(pygame.Color(255, 127, 0, 63), up.rect)
            down = self.get_target_bounds_at(pos_sub, Direction.DOWN)
            surface.fill(pygame.Color(0, 255, 127, 63), down.rect)

    def get_target_bounds_at(self, pos: tuple[int, int], direction: Direction) -> Bounds:
        x = pos[0]
        y = pos[1]
        if self.state == PlayerState.CROUCHING:
            return Bounds(x+8*16, y+14*16, 8*16, 9*16)
        match direction:
            case Direction.NONE:
                return Bounds(x+8*16, y+4*16, 8*16, 19*16)
            case Direction.UP:
                return Bounds(x+8*16, y+4*16, 8*16, 4*16)
            case Direction.DOWN:
                return Bounds(x+8*16, y+19*16, 8*16, 4*16)
            case Direction.RIGHT:
                return Bounds(x+12*16, y+4*16, 4*16, 14*16)
            case Direction.LEFT:
                return Bounds(x+8*16, y+4*16, 4*16, 14*16)

    def get_target_bounds_rect(self, direction: Direction) -> Bounds:
        """ Returns the bounds rect in pixels to check when moving in direction. """
        return self.get_target_bounds_at((self.x, self.y), direction)
