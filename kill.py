
import pygame
import typing

from imagemanager import ImageManager
from inputmanager import InputManager
from scene import Scene
from soundmanager import SoundManager


class KillScreen(Scene):
    previous: Scene
    next: typing.Callable[[], Scene]

    def __init__(self, previous: Scene, next: typing.Callable[[], Scene]):
        self.previous = previous
        self.next = next

    def update(self, input: InputManager, sounds: SoundManager) -> Scene:
        if input.is_ok_triggered():
            return self.next()
        return self

    def draw(self, surface: pygame.Surface, dest: pygame.Rect, images: ImageManager):
        red_color = pygame.Color(255, 0, 0, 127)
        red_surface = pygame.Surface(dest.size, pygame.SRCALPHA)
        red_surface.fill(red_color, dest)
        self.previous.draw(surface, dest, images)
        surface.blit(red_surface, dest)

        text = "DEAD"
        text_pos = (
            dest.width//2 - len(text) * 4,
            dest.height//2 - len(text) * 4)
        images.font.draw_string(surface, text_pos, text)
