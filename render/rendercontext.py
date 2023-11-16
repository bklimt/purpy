
import pygame

from constants import MAX_LIGHTS, SUBPIXELS
from render.spritebatch import SpriteBatch


class Light:
    position: tuple[int, int] = (0, 0)
    radius: float = 120.0

    def __init__(self, position: tuple[int, int], radius: float):
        self.position = position
        self.radius = radius


class RenderContext:
    render_size: tuple[int, int]
    render_area: pygame.Rect
    logical_area: pygame.Rect  # the render_area * subpixels

    hud_surface: pygame.Surface
    player_surface: pygame.Surface

    hud_batch: SpriteBatch
    player_batch: SpriteBatch

    dark: bool = False
    lights: list[Light]

    def __init__(self, render_size: tuple[int, int]):
        self.render_size: tuple[int, int] = render_size
        self.render_area = pygame.Rect(0, 0, render_size[0], render_size[1])
        self.logical_area = pygame.Rect(
            0, 0, render_size[0]*SUBPIXELS, render_size[1]*SUBPIXELS)

        self.hud_surface = pygame.Surface(render_size, pygame.SRCALPHA)
        self.foreground_surface = pygame.Surface(render_size, pygame.SRCALPHA)
        self.player_surface = pygame.Surface(render_size, pygame.SRCALPHA)
        self.background_surface = pygame.Surface(render_size, pygame.SRCALPHA)

        self.hud_batch = SpriteBatch(self.hud_surface)
        self.foreground_batch = SpriteBatch(self.foreground_surface)
        self.player_batch = SpriteBatch(self.player_surface)
        self.background_batch = SpriteBatch(self.background_surface)

        self.lights = []

    def clear(self):
        self.lights.clear()
        black = pygame.Color(0, 0, 0, 0)
        self.background_surface.fill(black, self.render_area)
        self.player_surface.fill(black, self.render_area)
        self.foreground_surface.fill(black, self.render_area)
        self.hud_surface.fill(black, self.render_area)

    def add_light(self, position: tuple[int, int], radius: float):
        self.lights.append(Light(position, radius))
