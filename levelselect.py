
import os
import pygame

from font import Font
from imagemanager import ImageManager
from inputmanager import InputManager
from level import Level
from renderoptions import RenderOptions
from scene import Scene
from soundmanager import SoundManager


class LevelSelect:
    parent: Scene | None
    directory: str
    files: list[str]
    current: int
    start: int = 0

    def __init__(self, parent: Scene | None, directory: str):
        self.parent = parent
        self.directory = os.path.normpath(directory)
        self.current = 0
        self.files = sorted(os.listdir(directory))

    def update(self, inputs: InputManager, sounds: SoundManager) -> Scene | None:
        if inputs.is_cancel_triggered():
            return self.parent
        if inputs.is_up_triggered():
            self.current = (self.current - 1) % len(self.files)
        if inputs.is_down_triggered():
            self.current = (self.current + 1) % len(self.files)
        if inputs.is_ok_triggered():
            new_path = os.path.join(self.directory, self.files[self.current])
            if os.path.isdir(new_path):
                return LevelSelect(self, new_path)
            else:
                return Level(self, new_path)
        return self

    def draw(self, surface: pygame.Surface, dest: pygame.Rect, images: ImageManager, options: RenderOptions):
        x = 4
        y = 4
        dir_str = os.path.join(self.directory, "")
        images.font.draw_string(surface, (x, y), dir_str)
        y += 12

        if self.current < self.start:
            # You scrolled up past what was visible.
            self.start = self.current
        if self.current >= self.start + 10:
            # You scrolled off the bottom.
            self.start = self.current - 10
        if self.start != 0:
            images.font.draw_string(surface, (x, y), ' ...')
        y += 12

        for i in range(self.start, self.start + 11):
            if i < 0 or i >= len(self.files):
                continue
            cursor = ' '
            if i == self.current:
                cursor = '>'
            images.font.draw_string(
                surface, (x, y), f'{cursor}{self.files[i]}')
            y += 12

        if self.start + 12 <= len(self.files):
            images.font.draw_string(surface, (x, y), ' ...')
