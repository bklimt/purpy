
import pygame

from render.spritebatch import SpriteBatch


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

    def sprite(self, index: int, layer: int, reverse: bool) -> pygame.Rect:
        column = index % self.columns
        row = index // self.columns
        if reverse:
            column = (self.columns - 1) - column
        row += layer
        x = column * self.sprite_width
        y = row * self.sprite_height
        return pygame.Rect(x, y, self.sprite_width, self.sprite_height)

    def blit(self,
             batch: SpriteBatch,
             pos: tuple[int, int],
             index: int = 0,
             layer: int = 0,
             reverse: bool = False):
        texture = self.surface
        if reverse:
            texture = self.reverse
        sprite = self.sprite(index, layer, reverse)
        dest = pygame.Rect(pos[0], pos[1], sprite.w * 16, sprite.h * 16)
        batch.draw(texture, dest, sprite)


class Animation:
    spritesheet: SpriteSheet
    index: int = 0
    frames: int
    frames_per_frame: int = 2
    timer: int

    def __init__(self, surface: pygame.Surface, sprite_width: int, sprite_height: int):
        self.spritesheet = SpriteSheet(surface, sprite_width, sprite_height)
        if surface.get_height() != sprite_height:
            raise Exception('animations can only have one row')
        self.frames = surface.get_width() // sprite_width
        self.timer = self.frames_per_frame

    def update(self):
        if self.timer == 0:
            self.index = (self.index + 1) % self.frames
            self.timer = self.frames_per_frame
        else:
            self.timer -= 1

    def blit(self, batch: SpriteBatch, pos: tuple[int, int], reverse: bool):
        self.spritesheet.blit(batch, pos, self.index, reverse)
