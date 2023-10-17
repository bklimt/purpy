
import pygame
from spritesheet import SpriteSheet
from tilemap import MapObject


class Spiral:
    sprite: SpriteSheet
    x: int
    y: int
    index: int = 0

    def __init__(self, obj: MapObject):
        texture = pygame.image.load('assets/spiral.png')
        self.sprite = SpriteSheet(texture, 24, 24)
        self.x = obj.x - 8
        self.y = obj.y - 8

    def update(self):
        self.index = (self.index + 1) % 12

    def draw(self, surface: pygame.Surface):
        self.sprite.blit(surface, (self.x, self.y), self.index, False)
