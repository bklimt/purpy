
import pygame


class SpriteSheet:
    surface: pygame.Surface
    reverse: pygame.Surface
    sprite_width: int
    sprite_height: int

    def __init__(self, surface: pygame.Surface, sprite_width: int, sprite_height: int):
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.surface = surface
        self.reverse = pygame.transform.flip(surface, True, False)

    def sprite(self, index: int, reverse: bool) -> pygame.Rect:
        if reverse:
            x = self.surface.get_width() - (index + 1) * self.sprite_width
            return pygame.Rect(x, 0, self.sprite_width, self.sprite_height)
        else:
            x = self.sprite_width * index
            return pygame.Rect(x, 0, self.sprite_width, self.sprite_height)

    def blit(self, surface: pygame.Surface, pos: tuple[int, int], index: int, reverse: bool):
        texture = self.surface
        if reverse:
            texture = self.reverse
        surface.blit(texture, pos, self.sprite(index, reverse))
