
import pygame

from constants import SUBPIXELS
from render.spritebatch import SpriteBatch
from tileset import ImageLoader, TileSet, load_tileset


class Font:
    tileset: TileSet
    char_width: int
    char_height: int

    def __init__(self, path: str, images: ImageLoader):
        # The firstgid doesn't matter, since there's no map.
        self.tileset = load_tileset(path, 0, images)
        self.char_width = 8 * SUBPIXELS
        self.char_height = 8 * SUBPIXELS

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
