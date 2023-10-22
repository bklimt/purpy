
from font import Font
from inputmanager import InputManager
from level import Level
import os
import pygame
from scene import Scene


class LevelSelect(Scene):
    parent: Scene | None
    directory: str
    files: list[str]
    current: int
    font: Font
    start: int = 0

    def __init__(self, parent: Scene | None, directory: str, font: Font):
        self.parent = parent
        self.directory = os.path.normpath(directory)
        self.current = 0
        self.font = font
        self.files = os.listdir(directory)

    def update(self, input: InputManager) -> Scene | None:
        if input.is_key_triggered(pygame.K_ESCAPE):
            return self.parent
        if input.is_key_triggered(pygame.K_UP):
            self.current = (self.current - 1) % len(self.files)
        if input.is_key_triggered(pygame.K_DOWN):
            self.current = (self.current + 1) % len(self.files)
        if input.is_key_triggered(pygame.K_RETURN):
            new_path = os.path.join(self.directory, self.files[self.current])
            if os.path.isdir(new_path):
                return LevelSelect(self, new_path, self.font)
            else:
                return Level(self, new_path, self.font)
        return self

    def draw(self, surface: pygame.Surface, dest: pygame.Rect):
        x = 4
        y = 4
        dir_str = os.path.join(self.directory, "")
        self.font.draw_string(surface, (x, y), dir_str)
        y += 12

        if self.current < self.start:
            # You scrolled up past what was visible.
            self.start = self.current
        if self.current >= self.start + 10:
            # You scrolled off the bottom.
            self.start = self.current - 10
        if self.start != 0:
            self.font.draw_string(surface, (x, y), ' ...')
        y += 12

        for i in range(self.start, self.start + 11):
            if i < 0 or i >= len(self.files):
                continue
            cursor = ' '
            if i == self.current:
                cursor = '>'
            self.font.draw_string(surface, (x, y), f'{cursor}{self.files[i]}')
            y += 12

        if self.start + 12 <= len(self.files):
            self.font.draw_string(surface, (x, y), ' ...')
