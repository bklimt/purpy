
import pygame

from enum import Enum
from random import randint

from spritesheet import SpriteSheet
from utils import Bounds, Direction

FRAMES_PER_FRAME = 8
IDLE_TIME = 240


class PlayerState(Enum):
    AIRBORNE = 1
    STANDING = 2
    CROUCHING = 3
    WALL_SLIDING = 4
    STOPPED = 5


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
        if self.state == PlayerState.AIRBORNE:
            index = 5
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
        self.sprite.blit(surface, pos, index, not self.facing_right)

    def get_target_bounds_rect_old(self, direction: Direction) -> pygame.Rect:
        """ Returns the bounds rect in pixels to check when moving in direction. """
        x = self.x // 16
        y = self.y // 16
        if self.state == PlayerState.CROUCHING:
            return pygame.Rect(x+8, y+14, 8, 9)
        match direction:
            case Direction.NONE:
                return pygame.Rect(x+8, y+4, 8, 19)
            case Direction.NORTH:
                return pygame.Rect(x+8, y+4, 8, 4)
            case Direction.SOUTH:
                return pygame.Rect(x+8, y+19, 8, 4)
            case Direction.EAST:
                return pygame.Rect(x+12, y+4, 4, 15)
            case Direction.WEST:
                return pygame.Rect(x+8, y+4, 4, 15)

    def get_target_bounds_rect(self, direction: Direction) -> Bounds:
        """ Returns the bounds rect in pixels to check when moving in direction. """
        if self.state == PlayerState.CROUCHING:
            return Bounds(self.x+8*16, self.y+14*16, 8*16, 9*16)
        match direction:
            case Direction.NONE:
                return Bounds(self.x+8*16, self.y+4*16, 8*16, 19*16)
            case Direction.NORTH:
                return Bounds(self.x+8*16, self.y+4*16, 8*16, 4*16)
            case Direction.SOUTH:
                return Bounds(self.x+8*16, self.y+19*16, 8*16, 4*16)
            case Direction.EAST:
                return Bounds(self.x+12*16, self.y+4*16, 4*16, 15*16)
            case Direction.WEST:
                return Bounds(self.x+8*16, self.y+4*16, 4*16, 15*16)
