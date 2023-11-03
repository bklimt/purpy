
import pygame

from renderoptions import RenderOptions


class RenderContext:
    logical_size: tuple[int, int]
    logical_area: pygame.Rect
    hud_surface: pygame.Surface
    foreground_surface: pygame.Surface
    player_surface: pygame.Surface
    background_surface: pygame.Surface
    options: RenderOptions

    def __init__(self, logical_size: tuple[int, int]):
        self.logical_size = logical_size
        self.logical_area = pygame.Rect(0, 0, logical_size[0], logical_size[1])
        self.hud_surface = pygame.Surface(logical_size, pygame.SRCALPHA)
        self.foreground_surface = pygame.Surface(logical_size, pygame.SRCALPHA)
        self.player_surface = pygame.Surface(logical_size, pygame.SRCALPHA)
        self.background_surface = pygame.Surface(logical_size, pygame.SRCALPHA)
        self.options = RenderOptions()

    def clear(self):
        self.options = RenderOptions()
        black = pygame.Color(0, 0, 0, 0)
        self.background_surface.fill(black, self.logical_area)
        self.player_surface.fill(black, self.logical_area)
        self.foreground_surface.fill(black, self.logical_area)
        self.hud_surface.fill(black, self.logical_area)
