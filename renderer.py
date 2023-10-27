
import pygame
import typing


class Renderer(typing.Protocol):
    def render(self, surface: pygame.Surface) -> None:
        raise Exception('abstract base class')
