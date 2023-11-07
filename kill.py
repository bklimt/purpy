
import pygame
import typing

from imagemanager import ImageManager
from inputmanager import InputManager
from rendercontext import RenderContext
from scene import Scene
from soundmanager import SoundManager


class KillScreen:
    previous: Scene
    next: typing.Callable[[], Scene]

    def __init__(self, previous: Scene, next: typing.Callable[[], Scene]):
        self.previous = previous
        self.next = next

    def update(self, inputs: InputManager, sounds: SoundManager) -> Scene:
        if inputs.is_ok_triggered():
            return self.next()
        return self

    def draw(self, context: RenderContext, images: ImageManager) -> None:
        dest = context.logical_area
        self.previous.draw(context, images)

        red_color = pygame.Color(255, 0, 0, 127)
        red_surface = pygame.Surface(dest.size, pygame.SRCALPHA)
        red_surface.fill(red_color, dest)
        surface = context.hud_surface
        surface.blit(red_surface, dest)
        text = "DEAD"
        text_pos = (
            dest.width//2 - len(text) * 4,
            dest.height//2 - len(text) * 4)
        images.font.draw_string(surface, text_pos, text)
