
import pygame

from enum import Enum
from random import randint

from constants import *
from imagemanager import ImageManager
from render.rendercontext import RenderContext
from render.spritebatch import SpriteBatch
from spritesheet import SpriteSheet
from utils import Direction


class PlayerState(Enum):
    FALLING = 1
    STANDING = 2
    CROUCHING = 3
    WALL_SLIDING = 4
    STOPPED = 5
    JUMPING = 6


class Player:
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
    frames_to_next_frame: int = PLAYER_FRAMES_PER_FRAME
    idle_counter: int = IDLE_TIME
    is_idle: bool = False
    is_dead: bool = False

    def __init__(self, images: ImageManager):
        self.texture = images.load_image('assets/sprites/skelly.png')
        self.sprite = SpriteSheet(self.texture, 24, 24)

    def draw(self, context: RenderContext, batch: SpriteBatch, pos: tuple[int, int]):
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
                self.frames_to_next_frame = PLAYER_FRAMES_PER_FRAME
            else:
                self.frames_to_next_frame -= 1
                if self.frames_to_next_frame <= 0:
                    self.frames_to_next_frame = PLAYER_FRAMES_PER_FRAME
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
                    self.frames_to_next_frame = PLAYER_FRAMES_PER_FRAME
                else:
                    self.frames_to_next_frame -= 1
                    if self.frames_to_next_frame <= 0:
                        self.frames_to_next_frame = PLAYER_FRAMES_PER_FRAME
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
            x_jiggle = randint(-SUBPIXELS, SUBPIXELS)
            y_jiggle = randint(-SUBPIXELS, SUBPIXELS)
            pos = (pos[0] + x_jiggle, pos[1] + y_jiggle)

        dest = pygame.Rect(pos[0], pos[1], 24 * SUBPIXELS, 24 * SUBPIXELS)

        self.sprite.blit(batch,
                         dest,
                         index=index,
                         reverse=not self.facing_right)

        if False:
            left = self.get_target_bounds_at(pos, Direction.LEFT)
            right = self.get_target_bounds_at(pos, Direction.RIGHT)
            up = self.get_target_bounds_at(pos, Direction.UP)
            down = self.get_target_bounds_at(pos, Direction.DOWN)
            batch.draw_rect(left, pygame.Color(255, 0, 255, 63))
            batch.draw_rect(right, pygame.Color(127, 127, 63, 63))
            batch.draw_rect(up, pygame.Color(255, 127, 0, 63))
            batch.draw_rect(down, pygame.Color(0, 255, 127, 63))

    def get_raw_target_bounds(self, direction: Direction) -> pygame.Rect:
        if self.state == PlayerState.CROUCHING:
            return pygame.Rect(8, 14, 8, 9)
        match direction:
            case Direction.NONE:
                return pygame.Rect(8, 4, 8, 19)
            case Direction.UP:
                return pygame.Rect(8, 4, 8, 4)
            case Direction.DOWN:
                return pygame.Rect(8, 19, 8, 4)
            case Direction.RIGHT:
                return pygame.Rect(12, 4, 4, 14)
            case Direction.LEFT:
                return pygame.Rect(8, 4, 4, 14)

    def get_target_bounds_rect(self, direction: Direction) -> pygame.Rect:
        """ Returns the bounds rect in pixels to check when moving in direction. """
        unscaled = self.get_raw_target_bounds(direction)
        return pygame.Rect(
            self.x + unscaled.x * SUBPIXELS,
            self.y + unscaled.y * SUBPIXELS,
            unscaled.w * SUBPIXELS,
            unscaled.h * SUBPIXELS)


class Player2(Player):
    def __init__(self, images: ImageManager):
        super().__init__(images)

    def next_frame(self):
        frame = self.frame
