
from enum import Enum
import pygame


class PlayerState(Enum):
    AIRBORNE = 1
    STANDING = 2
    CROUCHING = 3


class Player:
    # 24x24 sprite sheet
    texture: pygame.Surface
    state: PlayerState = PlayerState.STANDING

    def __init__(self):
        self.texture = pygame.image.load('assets/skelly.png')

    def draw(self, surface: pygame.Surface, pos: tuple[int, int]):
        # TODO(klimt): Map the state to a source rect...
        # IDLE, IDLE, IDLE, CROUCH, WAVE, JUMP, RUN, RUN, RUN, RUN
        area = pygame.Rect(0, 0, 24, 24)
        if self.state == PlayerState.AIRBORNE:
            area.x = 24 * 5
        surface.blit(self.texture, pos, area)
        # surface.fill(pygame.Color(255, 255, 0, 127),
        #              self.rect, pygame.BLEND_RGBA_MULT)

    # 8 4 7 19
    def rect(self, pos: tuple[int, int]) -> pygame.Rect:
        return pygame.Rect(pos[0]+8, pos[1]+4, 7, 19)
