
import pygame


class Component:
    area: pygame.Rect = pygame.Rect(0, 0, 8, 8)
    background_color: pygame.Color = pygame.Color(204, 204, 204)

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
