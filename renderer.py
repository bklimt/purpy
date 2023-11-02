
import pygame
import typing

from renderoptions import RenderOptions


class Renderer(typing.Protocol):
    def render(self, surface: pygame.Surface, options: RenderOptions) -> None:
        raise Exception('abstract base class')
