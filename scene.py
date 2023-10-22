
import pygame
import typing

from imagemanager import ImageManager
from inputmanager import InputManager
from soundmanager import SoundManager


class Scene(typing.Protocol):
    def update(self, input: InputManager, sounds: SoundManager) -> 'Scene | None':
        raise Exception('abstract base class')

    def draw(self, surface: pygame.Surface, dest: pygame.Rect, images: ImageManager) -> None:
        raise Exception('abstract base class')
