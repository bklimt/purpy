
import os

# Import the whole module to avoid a circular reference.
import level

from imagemanager import ImageManager
from inputmanager import InputSnapshot
from render.rendercontext import RenderContext
from scene import Scene
from soundmanager import SoundManager


class LevelSelect:
    previous: Scene | None
    directory: str
    files: list[str]
    current: int
    start: int = 0
    images: ImageManager

    def __init__(self, parent: Scene | None, directory: str, images: ImageManager):
        self.previous = parent
        self.directory = os.path.normpath(directory)
        self.current = 0
        self.files = sorted(os.listdir(directory))
        self.images = images

    def parent(self) -> Scene | None:
        return self.previous

    def update(self, inputs: InputSnapshot, images: ImageManager, sounds: SoundManager) -> Scene | None:
        if inputs.cancel:
            return self.previous
        if inputs.menu_up:
            self.current = (self.current - 1) % len(self.files)
        if inputs.menu_down:
            self.current = (self.current + 1) % len(self.files)
        if inputs.ok:
            new_path = os.path.join(self.directory, self.files[self.current])
            if os.path.isdir(new_path):
                return LevelSelect(self, new_path, self.images)
            else:
                return level.Level(self, new_path, self.images)
        return self

    def draw(self, context: RenderContext, images: ImageManager) -> None:
        batch = context.hud_batch
        font_height = images.font.char_height
        line_spacing = font_height // 2

        x = line_spacing
        y = line_spacing
        dir_str = os.path.join(self.directory, "")
        images.font.draw_string(batch, (x, y), dir_str)
        y += (font_height + line_spacing)

        if self.current < self.start:
            # You scrolled up past what was visible.
            self.start = self.current
        if self.current >= self.start + 10:
            # You scrolled off the bottom.
            self.start = self.current - 10
        if self.start != 0:
            images.font.draw_string(batch, (x, y), ' ...')
        y += (font_height + line_spacing)

        for i in range(self.start, self.start + 11):
            if i < 0 or i >= len(self.files):
                continue
            cursor = ' '
            if i == self.current:
                cursor = '>'
            images.font.draw_string(
                batch, (x, y), f'{cursor}{self.files[i]}')
            y += (font_height + line_spacing)

        if self.start + 12 <= len(self.files):
            images.font.draw_string(batch, (x, y), ' ...')
