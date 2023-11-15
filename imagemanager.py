
from font import Font


class ImageManager:
    font: Font

    def __init__(self, scale: int):
        self.font = Font('assets/8bitfont.tsx', scale)
