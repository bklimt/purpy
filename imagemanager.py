
import pygame

from constants import USE_OPENGL
from font import Font


class ImageManager:
    font: Font

    def __init__(self):
        self.font = Font('assets/8bitfont.tsx', self)

    def load_image(self, path: str) -> pygame.Surface:
        return pygame.image.load(path)
