
import pygame


class PygameRenderer:
    game_window: pygame.Surface
    scaled_back_buffer: pygame.Surface
    scaled_back_buffer_dest: pygame.Rect
    window_rect: pygame.Rect

    def __init__(self, _logical: pygame.Rect, destination: pygame.Rect, window: pygame.Rect):
        self.window_rect = window
        self.game_window = pygame.display.set_mode(window.size)

        self.scaled_back_buffer_dest = destination
        self.scaled_back_buffer = pygame.Surface(
            self.scaled_back_buffer_dest.size)

    def render(self, surface: pygame.Surface):
        # Clear the window with black.
        # Scale the back buffer to the right size.
        pygame.transform.scale(
            surface,
            self.scaled_back_buffer_dest.size,
            self.scaled_back_buffer)
        # Copy the back buffer to the window.
        self.game_window.fill((0, 0, 0), self.window_rect)
        self.game_window.blit(self.scaled_back_buffer,
                              self.scaled_back_buffer_dest)

        pygame.display.update()
