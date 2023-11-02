
import pygame
import typing

from imagemanager import ImageManager
from inputmanager import InputManager
from renderoptions import RenderOptions
from soundmanager import SoundManager


class Scene(typing.Protocol):
    def update(self, inputs: InputManager, sounds: SoundManager) -> 'Scene | None':
        raise Exception('abstract base class')

    def draw(self, surface: pygame.Surface, dest: pygame.Rect, images: ImageManager, options: RenderOptions) -> None:
        raise Exception('abstract base class')
