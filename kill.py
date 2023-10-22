
import pygame
from font import Font
from inputmanager import InputManager
import pygame
from scene import Scene
from typing import Callable


class KillScreen(Scene):
    font: Font
    previous: Scene
    next: Callable[[], Scene]

    def __init__(self, font: Font, previous: Scene, next: Callable[[], Scene]):
        self.previous = previous
        self.font = font
        self.next = next

    def update(self, input: InputManager) -> Scene:
        if input.is_ok_triggered():
            return self.next()
        return self

    def draw(self, surface: pygame.Surface, dest: pygame.Rect):
        red_color = pygame.Color(255, 0, 0, 127)
        red_surface = pygame.Surface(dest.size, pygame.SRCALPHA)
        red_surface.fill(red_color, dest)
        self.previous.draw(surface, dest)
        surface.blit(red_surface, dest)

        text = "DEAD"
        text_pos = (
            dest.width//2 - len(text) * 4,
            dest.height//2 - len(text) * 4)
        self.font.draw_string(surface, text_pos, text)
