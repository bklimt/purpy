
import pygame

from gui.bordercontainer import BorderContainer
from gui.component import Component
from inputmanager import InputManager


class Window(BorderContainer):
    def __init__(self):
        super().__init__()
        title_bar = Component()
        title_bar.background_color = pygame.Color(0, 0, 127)

        close_button = Component()
        close_button.background_color = pygame.Color(127, 127, 127)

        top_bar = BorderContainer()
        top_bar.center = title_bar
        top_bar.right = close_button

        self.top = top_bar

    def update(self, inputs: InputManager) -> None:
        pass
