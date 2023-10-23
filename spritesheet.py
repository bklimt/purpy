
import pygame


class SpriteSheet:
    surface: pygame.Surface
    reverse: pygame.Surface
    sprite_width: int
    sprite_height: int
    columns: int

    def __init__(self, surface: pygame.Surface, sprite_width: int, sprite_height: int):
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.surface = surface
        self.reverse = pygame.transform.flip(surface, True, False)
        self.columns = surface.get_width() // sprite_width

    def sprite(self, index: int, reverse: bool) -> pygame.Rect:
        column = index % self.columns
        row = index // self.columns
        if reverse:
            column = (self.columns - 1) - column
        x = column * self.sprite_width
        y = row * self.sprite_height
        return pygame.Rect(x, y, self.sprite_width, self.sprite_height)

    def blit(self, surface: pygame.Surface, pos: tuple[int, int], index: int, reverse: bool):
        texture = self.surface
        if reverse:
            texture = self.reverse
        surface.blit(texture, pos, self.sprite(index, reverse))
