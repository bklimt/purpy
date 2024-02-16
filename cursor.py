
import pygame

from constants import SUBPIXELS
from imagemanager import ImageManager
from inputmanager import InputSnapshot
from render.rendercontext import RenderContext
from render.spritebatch import SpriteBatch


class Cursor:
    x: int = 0
    y: int = 0
    sprite: pygame.Surface

    def __init__(self, images: ImageManager):
        self.sprite = images.load_image('assets/cursor.png')

    def draw(self, context: RenderContext, batch: SpriteBatch):
        batch.draw(self.sprite, pygame.Rect(self.x, self.y, 8, 8))

    def update(self, input: InputSnapshot):
        self.x = input.mouse_x * SUBPIXELS
        self.y = input.mouse_y * SUBPIXELS
