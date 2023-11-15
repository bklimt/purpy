
import pygame

from render.spritebatch import SpriteBatch

MAX_LIGHTS = 20


class Light:
    position: tuple[int, int] = (0, 0)
    radius: float = 120.0

    def __init__(self, position: tuple[int, int], radius: float):
        self.position = position
        self.radius = radius


class RenderContext:
    logical_size: tuple[int, int]
    logical_area: pygame.Rect

    hud_surface: pygame.Surface
    foreground_surface: pygame.Surface
    player_surface: pygame.Surface
    background_surface: pygame.Surface

    foreground_batch: SpriteBatch
    player_batch: SpriteBatch
    background_batch: SpriteBatch

    dark: bool = False
    lights: list[Light]
    subpixels: int = 16

    def __init__(self, logical_size: tuple[int, int]):
        self.logical_size = logical_size
        self.logical_area = pygame.Rect(0, 0, logical_size[0], logical_size[1])

        self.hud_surface = pygame.Surface(logical_size, pygame.SRCALPHA)
        self.foreground_surface = pygame.Surface(logical_size, pygame.SRCALPHA)
        self.player_surface = pygame.Surface(logical_size, pygame.SRCALPHA)
        self.background_surface = pygame.Surface(logical_size, pygame.SRCALPHA)

        self.hud_batch = SpriteBatch(self.hud_surface)
        self.foreground_batch = SpriteBatch(self.foreground_surface)
        self.player_batch = SpriteBatch(self.player_surface)
        self.background_batch = SpriteBatch(self.background_surface)

        self.lights = []

    def clear(self):
        self.lights.clear()
        black = pygame.Color(0, 0, 0, 0)
        self.background_surface.fill(black, self.logical_area)
        self.player_surface.fill(black, self.logical_area)
        self.foreground_surface.fill(black, self.logical_area)
        self.hud_surface.fill(black, self.logical_area)

    def add_light(self, position: tuple[int, int], radius: float):
        self.lights.append(Light(position, radius))
