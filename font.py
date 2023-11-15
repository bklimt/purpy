
import pygame

from render.spritebatch import SpriteBatch
from tileset import load_tileset, TileSet


class Font:
    tileset: TileSet
    scale: int
    char_width: int
    char_height: int

    def __init__(self, path: str, scale: int = 1):
        self.tileset = load_tileset(path)
        self.scale = scale
        self.char_width = 8 * self.scale
        self.char_height = 8 * self.scale

    def draw_string(self, batch: SpriteBatch, pos: tuple[int, int], s: str):
        for ch in s:
            c = ord(ch)
            if c > 127:
                c = 127
            area = self.tileset.get_source_rect(c)
            dest = pygame.Rect(
                pos[0], pos[1], self.char_width, self.char_height)
            if dest.bottom <= 0 or dest.right <= 0:
                continue
            batch.draw(self.tileset.surface, dest, area)
            pos = (pos[0] + self.char_width, pos[1])
