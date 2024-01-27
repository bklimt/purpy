
import pygame

from constants import *
from gameobject.platforms import PlatformBase
from imagemanager import ImageManager
from render.rendercontext import RenderContext
from render.spritebatch import SpriteBatch
from soundmanager import Sound, SoundManager
from spritesheet import SpriteSheet
from switchstate import SwitchState
from tilemap import MapObject, TileMap
from utils import assert_str


class Button(PlatformBase):
    sprite: SpriteSheet
    level: int = 0
    original_y: int
    clicked: bool = False
    button_type: str
    was_occupied: bool
    color: str

    def __init__(self, obj: MapObject, tilemap: TileMap, images: ImageManager):
        super().__init__(obj, tilemap)
        self.original_y = self.y
        # Move down by a whole pixel while on a button.
        self.dy = SUBPIXELS
        self.color = assert_str(obj.properties.get('color', 'red'))
        surface = images.load_image(self.get_image_path(obj))
        self.sprite = SpriteSheet(surface, 8, 8)
        self.button_type = assert_str(
            obj.properties.get('button_type', 'toggle'))

    def get_image_path(self, obj: MapObject):
        color = self.color
        if color == '!white':
            color = 'black'
        return f'assets/sprites/buttons/{color}.png'

    def draw(self, context: RenderContext, batch: SpriteBatch, offset: tuple[int, int]):
        x = self.x + offset[0]
        y = self.original_y + offset[1]
        dest = pygame.Rect(x, y, self.width, self.height)
        self.sprite.blit(batch, dest, self.level // BUTTON_DELAY)

    def update(self, switches: SwitchState, sounds: SoundManager):
        was_clicked = self.clicked

        if self.button_type == 'smart':
            self.clicked = switches.is_condition_true(self.color)

        if self.occupied and not self.was_occupied:
            if self.button_type == 'oneshot':
                self.clicked = True
            elif self.button_type == 'toggle':
                self.clicked = not self.clicked
            elif self.button_type == 'smart':
                self.clicked = True

        self.was_occupied = self.occupied

        if self.button_type == 'momentary':
            self.clicked = self.occupied

        if self.clicked:
            if self.level < BUTTON_MAX_LEVEL:
                self.level += 1
        else:
            if self.level > 0:
                self.level -= 1

        self.y = self.original_y + ((self.level * SUBPIXELS) // BUTTON_DELAY)

        if self.clicked != was_clicked:
            sounds.play(Sound.CLICK)
            if self.button_type == 'smart':
                if self.clicked and self.occupied:
                    switches.apply_command(self.color)
            elif self.clicked or self.button_type != 'oneshot':
                switches.toggle(self.color)
