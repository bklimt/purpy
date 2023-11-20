
import pygame

from render.rendercontext import RenderContext


class PygameRenderer:
    game_window: pygame.Surface
    back_buffer: pygame.Surface
    scaled_back_buffer: pygame.Surface
    scaled_back_buffer_dest: pygame.Rect
    window_rect: pygame.Rect

    def __init__(self, render_area: pygame.Rect, destination: pygame.Rect, window: pygame.Rect):
        self.window_rect = window
        self.game_window = pygame.display.set_mode(window.size)

        self.back_buffer = pygame.Surface(render_area.size)
        self.scaled_back_buffer_dest = destination
        self.scaled_back_buffer = pygame.Surface(
            self.scaled_back_buffer_dest.size)

    def render(self, context: RenderContext):
        self.back_buffer.fill((0, 0, 0))
        self.back_buffer.blit(context.player_surface, (0, 0))
        self.back_buffer.blit(context.hud_surface, (0, 0))

        # Scale the back buffer to the right size.
        pygame.transform.scale(
            self.back_buffer,
            self.scaled_back_buffer_dest.size,
            self.scaled_back_buffer)

        # Clear the window with black.
        self.game_window.fill((0, 0, 0), self.window_rect)

        # Copy the back buffer to the window.
        self.game_window.blit(self.scaled_back_buffer,
                              self.scaled_back_buffer_dest)

        pygame.display.update()
