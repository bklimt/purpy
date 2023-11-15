
import pygame
import typing

from imagemanager import ImageManager
from inputmanager import InputManager
from render.rendercontext import RenderContext
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
        # TODO: Figure out what logical area means...
        dest = pygame.Rect(dest.x * 16, dest.y * 16, dest.w * 16, dest.h * 16)
        self.previous.draw(context, images)

        red_color = pygame.Color(255, 0, 0, 127)
        context.hud_batch.draw_rect(dest, red_color)

        # TODO: Get this from the font.
        char_width = 8*16
        text = "DEAD"
        text_pos = (
            dest.width//2 - len(text) * (char_width//2),
            dest.height//2 - len(text) * (char_width//2))
        images.font.draw_string(context.hud_batch, text_pos, text)
