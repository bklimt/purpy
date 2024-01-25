
import pygame
import typing

from imagemanager import ImageManager
from inputmanager import InputSnapshot
from render.rendercontext import RenderContext
from scene import Scene
from soundmanager import SoundManager


class KillScreen:
    previous: Scene
    next: typing.Callable[[], Scene]

    def __init__(self, previous: Scene, next: typing.Callable[[], Scene]):
        self.previous = previous
        self.next = next

    def update(self, inputs: InputSnapshot, sounds: SoundManager) -> Scene:
        if inputs.ok:
            return self.next()
        return self

    def draw(self, context: RenderContext, images: ImageManager) -> None:
        dest = context.logical_area
        self.previous.draw(context, images)

        red_color = pygame.Color(255, 0, 0, 127)
        context.hud_batch.draw_rect(dest, red_color)

        text = "DEAD"
        text_pos = (
            dest.width//2 - len(text) * (images.font.char_width//2),
            dest.height//2 - len(text) * (images.font.char_width//2))
        images.font.draw_string(context.hud_batch, text_pos, text)
