
import pygame

from inputmanager import InputManager


class EdgeSpacing:
    left: int
    right: int
    top: int
    bottom: int

    def __init__(self, n: int = 0):
        self.left = n
        self.right = n
        self.top = n
        self.bottom = n

    @property
    def h(self) -> int:
        return self.left + self.right

    @property
    def v(self) -> int:
        return self.top + self.bottom


class Component:
    area: pygame.Rect = pygame.Rect(0, 0, 8, 8)
    background_color: pygame.Color = pygame.Color(204, 204, 204)

    margin: EdgeSpacing = EdgeSpacing()
    border: EdgeSpacing = EdgeSpacing()
    padding: EdgeSpacing = EdgeSpacing()

    def __init__(self):
        pass

    def get_preferred_size(self) -> tuple[int, int]:
        return (50,  50)

    def get_preferred_width(self, height: int) -> int:
        return self.get_preferred_size()[0]

    def get_preferred_height(self, width: int) -> int:
        return self.get_preferred_size()[1]

    def set_area(self, area: pygame.Rect) -> None:
        self.area = area.copy()

    def draw(self, surface: pygame.Surface) -> None:
        area = self.area.copy()

        area.width -= self.margin.left
        area.width -= self.margin.right
        area.height -= self.margin.top
        area.height -= self.margin.bottom
        area.top += self.margin.top
        area.left += self.margin.left
        pygame.draw.rect(surface, '#000000', area)

        area.width -= self.border.left
        area.width -= self.border.right
        area.height -= self.border.top
        area.height -= self.border.bottom
        area.top += self.border.top
        area.left += self.border.left
        surface.fill(self.background_color, area)

    def edge_spacing(self) -> EdgeSpacing:
        edge = EdgeSpacing()
        edge.top = self.margin.top + self.border.top + self.padding.top
        edge.bottom = self.margin.bottom + self.border.top + self.padding.top
        edge.left = self.margin.left + self.border.left + self.padding.left
        edge.right = self.margin.right + self.border.right + self.padding.right
        return edge
