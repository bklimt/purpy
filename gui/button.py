
import typing

from gui.component import Component


class Button(Component):
    onclick: typing.Callable[[tuple[int, int]], None] = lambda _: None

    def __init__(self):
        super().__init__()

    def mouse_clicked(self, pos: tuple[int, int]) -> None:
        super().mouse_clicked(pos)
        self.onclick(pos)
