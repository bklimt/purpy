
import pygame


class SpriteBatch:
    canvas: pygame.Surface

    def __init__(self, canvas: pygame.Surface):
        self.canvas = canvas

    def draw(self,
             texture: pygame.Surface,
             dest: pygame.Rect,
             src: pygame.Rect | None = None):
        self.canvas.blit(texture, dest, area=src)
