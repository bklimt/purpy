
import pygame
import typing

from rendercontext import RenderContext


class Renderer(typing.Protocol):
    def render(self, surface: pygame.Surface, context: RenderContext) -> None:
        raise Exception('abstract base class')
