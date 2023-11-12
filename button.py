
import pygame

from platforms import PlatformBase
from soundmanager import Sound, SoundManager
from spritesheet import SpriteSheet
from switchstate import SwitchState
from tilemap import MapObject
from tileset import TileSet
from utils import assert_str

BUTTON_DELAY = 2
MAX_LEVEL = BUTTON_DELAY * 3


class Button(PlatformBase):
    sprite: SpriteSheet
    level: int = 0
    original_y: int
    clicked: bool = False
    button_type: str
    was_occupied: bool
    color: str

    def __init__(self, obj: MapObject, tileset: TileSet):
        super().__init__(obj, tileset)
        self.original_y = self.y
        self.color = assert_str(obj.properties.get('color', 'red'))
        surface = pygame.image.load(self.get_image_path(obj))
        self.sprite = SpriteSheet(surface, 8, 8)
        self.button_type = assert_str(
            obj.properties.get('button_type', 'toggle'))

    def get_image_path(self, obj: MapObject):
        color = self.color
        if color == '!white':
            color = 'black'
        return f'assets/sprites/buttons/{color}.png'

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]):
        x = self.x//16 + offset[0]
        y = self.original_y//16 + offset[1]
        self.sprite.blit(surface, (x, y), self.level // BUTTON_DELAY)

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
            if self.level < MAX_LEVEL:
                self.level += 1
        else:
            if self.level > 0:
                self.level -= 1

        self.y = self.original_y + ((self.level * 16) // BUTTON_DELAY)

        if self.clicked != was_clicked:
            sounds.play(Sound.CLICK)
            if self.button_type == 'smart':
                if self.clicked and self.occupied:
                    switches.apply_command(self.color)
            elif self.clicked or self.button_type != 'oneshot':
                switches.toggle(self.color)
