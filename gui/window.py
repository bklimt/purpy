
import pygame

from gui.bordercontainer import BorderContainer
from gui.button import Button
from gui.component import Component


class Window(BorderContainer):
    title_bar: Component
    relative_click_position: tuple[int, int]

    def __init__(self):
        super().__init__()
        self.title_bar = Component()
        self.title_bar.background_color = pygame.Color(0, 0, 127)

        close_button = Button()
        close_button.background_color = pygame.Color(127, 127, 127)
        close_button.onclick = lambda _: print('close window')

        top_bar = BorderContainer()
        top_bar.center = self.title_bar
        top_bar.right = close_button

        self.top = top_bar

    def get_component_at(self, pos: tuple[int, int]) -> Component | None:
        target = super().get_component_at(pos)
        if target == self.title_bar:
            return self
        return target

    def mouse_pressed(self, pos: tuple[int, int]) -> None:
        super().mouse_pressed(pos)
        area = self.area
        self.relative_click_position = (area.x - pos[0], area.y - pos[1])

    def mouse_dragged(self, pos: tuple[int, int]) -> None:
        super().mouse_dragged(pos)
        self.area.x = self.relative_click_position[0] + pos[0]
        self.area.y = self.relative_click_position[1] + pos[1]
        # TODO: Move rather than relayout.
        self.set_area(self.area)
