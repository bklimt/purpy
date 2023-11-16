
import pygame

from constants import SUBPIXELS


class SpriteBatch:
    canvas: pygame.Surface

    def __init__(self, canvas: pygame.Surface):
        self.canvas = canvas

    def draw(self,
             texture: pygame.Surface,
             dest: pygame.Rect,
             src: pygame.Rect | None = None):
        s = SUBPIXELS
        scaled = pygame.Rect(dest.x//s, dest.y//s, dest.w//s, dest.h//s)
        overlap = scaled.clip(self.canvas.get_rect())
        if overlap.w == 0:
            return
        self.canvas.blit(texture, scaled, area=src)

    def draw_rect(self, dest: pygame.Rect, color: pygame.Color | str):
        if dest.bottom < 0:
            return
        if dest.y < 0:
            dest = pygame.Rect(dest.x, 0, dest.w, dest.h + dest.y)
        s = SUBPIXELS
        dest = pygame.Rect(dest.x//s, dest.y//s, dest.w//s, dest.h//s)
        self.canvas.fill(color, dest)
