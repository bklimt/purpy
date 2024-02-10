import pygame

from enum import IntEnum

from constants import SUBPIXELS
from font import Font
from imagemanager import ImageManager
from inputmanager import InputSnapshot
from render.rendercontext import RenderContext
from render.spritebatch import SpriteBatch
from scene import Scene
from soundmanager import SoundManager
from spritesheet import SpriteSheet
from tilemap import MapObject
from utils import inside


class ButtonState(IntEnum):
    NORMAL = 0
    HOVER = 1
    MOUSE_CLICK = 2
    GAMEPAD_CLICK = 3


class UiButton:
    x: int
    y: int
    width: int
    height: int
    spritesheet: SpriteSheet
    state = ButtonState.NORMAL
    clicking: bool
    label: str
    action: str | None

    def __init__(self, object: MapObject, tilewidth: int, tileheight: int, images: ImageManager):
        surface = images.load_image('assets/uibutton.png')
        self.spritesheet = SpriteSheet(surface, tilewidth, tileheight)
        self.x = object.x * SUBPIXELS
        self.y = object.y * SUBPIXELS
        self.width = object.width * SUBPIXELS
        self.height = object.height * SUBPIXELS
        self.label = object.properties.label
        self.action = object.properties.uibutton

    def update(self, selected: bool, inputs: InputSnapshot, sounds: SoundManager) -> str | None:
        """ Returns True if clicked. """
        clicked = False
        point = (inputs.mouse_x * SUBPIXELS, inputs.mouse_y * SUBPIXELS)
        mouse_inside = inside(pygame.Rect(
            self.x, self.y, self.width, self.height), point)

        if self.state == ButtonState.MOUSE_CLICK:
            if not inputs.mouse_down:
                if mouse_inside:
                    print("CLICK!")
                    clicked = True
                self.state = ButtonState.NORMAL
        elif self.state == ButtonState.GAMEPAD_CLICK:
            if not inputs.ok_down:
                print("CLICK!")
                clicked = True
                self.state = ButtonState.NORMAL
        elif selected and inputs.ok_down:
            self.state = ButtonState.GAMEPAD_CLICK
        elif mouse_inside and inputs.mouse_down:
            self.state = ButtonState.MOUSE_CLICK
        elif selected or mouse_inside:
            self.state = ButtonState.HOVER
        else:
            self.state = ButtonState.NORMAL

        if clicked:
            return self.action
        else:
            return None

    def draw(self, context: RenderContext, batch: SpriteBatch, font: Font):
        w = self.spritesheet.sprite_width * SUBPIXELS
        h = self.spritesheet.sprite_height * SUBPIXELS
        cols = self.width // w
        rows = self.height // h
        for row in range(rows):
            for col in range(cols):
                x = self.x + col * w
                y = self.y + row * h
                dest = pygame.Rect(x, y, w, h)

                index = 1
                if col == 0:
                    index = 0
                elif col == cols - 1:
                    index = 2

                index = index + 3 * min(self.state, 2)

                layer = 1
                if row == 0:
                    layer = 0
                elif row == rows - 1:
                    layer = 2

                self.spritesheet.blit(batch, dest, index, layer)

        label_x = self.x + font.char_width
        label_y = self.y + font.char_height
        if self.state == ButtonState.MOUSE_CLICK or self.state == ButtonState.GAMEPAD_CLICK:
            label_x += 2 * SUBPIXELS
            label_y += 2 * SUBPIXELS
        font.draw_string(batch, (label_x, label_y), self.label)
        # underline = '_' * len(self.label)
        # font.draw_string(batch, (label_x, label_y + 2 * SUBPIXELS), underline)
