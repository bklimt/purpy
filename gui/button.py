
import pygame

from component import Component


class Button(Component):
    text: str
    width: int
    height: int

    def __init__(self, text: str, width: int, height: int):
        super().__init__()
        self.text = text
        self.width = width
        self.height = height

    def get_preferred_size(self) -> tuple[int, int]:
        return (self.width, self.height)
