
import input
import pygame
import tilemap


class Level:
    x: int = 0
    y: int = 0
    map: tilemap.TileMap

    def __init__(self):
        self.map = tilemap.load_map('assets/map.tmx')

    def update(self):
        if input.is_key_down(pygame.K_w):
            self.y += 2
        if input.is_key_down(pygame.K_a):
            self.x += 2
        if input.is_key_down(pygame.K_s):
            self.y -= 2
        if input.is_key_down(pygame.K_d):
            self.x -= 2

    def draw(self, surface: pygame.Surface, dest: pygame.Rect):
        self.map.draw(surface, dest, (self.x, self.y))
