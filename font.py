
import pygame
from tileset import load_tileset, TileSet


class Font:
    tileset: TileSet

    def __init__(self, path: str):
        self.tileset = load_tileset(path)

    def draw_string(self, surface: pygame.Surface, pos: tuple[int, int], s: str):
        for ch in s:
            c = ord(ch)
            if c > 127:
                c = 127
            area = self.tileset.get_source_rect(c+1)
            surface.blit(self.tileset.surface, pos, area)
            pos = (pos[0]+8, pos[1])
