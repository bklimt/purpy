
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
        self.canvas.fill(color, dest)
