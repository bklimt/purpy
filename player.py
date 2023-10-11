
import pygame


class Player:
    texture: pygame.Surface

    def __init__(self):
        self.texture = pygame.image.load('assets/skelly.png')

    def draw(self, surface: pygame.Surface, pos: tuple[int, int]):
        surface.blit(self.texture, pos)
        # surface.fill(pygame.Color(255, 255, 0, 127),
        #              self.rect, pygame.BLEND_RGBA_MULT)

    def rect(self, pos: tuple[int, int]) -> pygame.Rect:
        return pygame.Rect(pos[0], pos[1], self.texture.get_width(), self.texture.get_height())
