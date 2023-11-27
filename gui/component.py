
import pygame


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
        surface.fill(self.background_color, self.area)

    def edge_spacing(self) -> EdgeSpacing:
        edge = EdgeSpacing()
        edge.top = self.margin.top + self.border.top + self.padding.top
        edge.bottom = self.margin.bottom + self.border.top + self.padding.top
        edge.left = self.margin.left + self.border.left + self.padding.left
        edge.right = self.margin.right + self.border.right + self.padding.right
        return edge
