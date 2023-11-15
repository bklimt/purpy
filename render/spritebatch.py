
import pygame


class SpriteBatch:
    canvas: pygame.Surface

    def __init__(self, canvas: pygame.Surface):
        self.canvas = canvas

    def draw(self,
             texture: pygame.Surface,
             dest: pygame.Rect,
             src: pygame.Rect | None = None):
        dest = pygame.Rect(dest.x//16, dest.y//16, dest.w//16, dest.h//16)
        self.canvas.blit(texture, dest, area=src)

    def draw_rect(self, dest: pygame.Rect, color: pygame.Color | str):
        if dest.bottom < 0:
            return
        if dest.y < 0:
            dest = pygame.Rect(dest.x, 0, dest.w, dest.h + dest.y)
        dest = pygame.Rect(dest.x//16, dest.y//16, dest.w//16, dest.h//16)
        self.canvas.fill(color, dest)
