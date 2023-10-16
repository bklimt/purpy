
from inputmanager import InputManager
import pygame


class Scene:
    def __init__(self):
        raise Exception('abstract base class')

    def update(self, input: InputManager) -> 'Scene':
        raise Exception('abstract base class')

    def draw(self, surface: pygame.Surface, dest: pygame.Rect):
        pass
