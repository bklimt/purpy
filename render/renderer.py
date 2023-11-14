
import pygame
import typing

from render.rendercontext import RenderContext


class Renderer(typing.Protocol):
    def render(self, context: RenderContext) -> None:
        raise Exception('abstract base class')
