
import pygame

from render.spritebatch import SpriteBatch
from tileset import load_tileset, TileSet


class Font:
    tileset: TileSet
    scale: int

    def __init__(self, path: str, scale: int = 1):
        self.tileset = load_tileset(path)
        self.scale = scale
        # TODO: Replace this.
        self.scale = 16

    def draw_string(self, batch: SpriteBatch, pos: tuple[int, int], s: str):
        char_height = 8 * self.scale
        char_width = 8 * self.scale
        for ch in s:
            c = ord(ch)
            if c > 127:
                c = 127
            area = self.tileset.get_source_rect(c)
            dest = pygame.Rect(pos[0], pos[1], char_width, char_height)
            batch.draw(self.tileset.surface, dest, area)
            pos = (pos[0] + char_width, pos[1])
