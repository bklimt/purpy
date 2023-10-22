
from font import Font
from inputmanager import InputManager
from level import Level
from levelselect import LevelSelect
import os
import pygame
from scene import Scene
import sys

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
LOGICAL_WIDTH = 320
LOGICAL_HEIGHT = 180
FRAME_RATE = 60

pygame.init()

BACK_BUFFER: pygame.Surface = pygame.Surface(
    (LOGICAL_WIDTH, LOGICAL_HEIGHT))
GAME_WINDOW: pygame.Surface = pygame.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT))


def compute_buffer_dest():
    target_aspect_ratio = LOGICAL_WIDTH / LOGICAL_HEIGHT
    needed_width = target_aspect_ratio * WINDOW_HEIGHT
    if needed_width <= WINDOW_WIDTH:
        # The window is wider than needed.
        return pygame.Rect((WINDOW_WIDTH - needed_width)//2, 0, needed_width, WINDOW_HEIGHT)
    else:
        # The window is taller than needed.
        needed_height = WINDOW_WIDTH / target_aspect_ratio
        return pygame.Rect(0, (WINDOW_HEIGHT - needed_height)//2, WINDOW_WIDTH, needed_height)


BACK_BUFFER_SRC = pygame.Rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT)
BACK_BUFFER_DST = compute_buffer_dest()

SCALED_BACK_BUFFER_SIZE = (BACK_BUFFER_DST.width, BACK_BUFFER_DST.height)
SCALED_BACK_BUFFER = pygame.Surface(SCALED_BACK_BUFFER_SIZE)

pygame.display.set_caption('purpy')


class Game:
    clock = pygame.time.Clock()
    input_manager = InputManager()
    font: Font
    scene: Scene | None

    def __init__(self):
        self.font = Font('assets/8bitfont.tsx')

        if len(sys.argv) > 1:
            self.scene = Level(None, sys.argv[1], self.font)
        else:
            self.scene = LevelSelect(None, 'assets/levels', self.font)

    def update(self) -> bool:
        """ Returns True if the game should keep running. """
        if self.scene is None:
            return False

        # Update the actual game logic.
        self.scene = self.scene.update(self.input_manager)
        if self.scene is None:
            return False

        self.input_manager.update()

        # Clear the back buffer with solid black.
        BACK_BUFFER.fill((0, 0, 0), BACK_BUFFER_SRC)
        # Draw the scene.
        self.scene.draw(BACK_BUFFER, pygame.Rect(
            0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT))
        # Clear the window with black.
        # Scale the back buffer to the right size.
        pygame.transform.scale(
            BACK_BUFFER, SCALED_BACK_BUFFER_SIZE, SCALED_BACK_BUFFER)
        # Copy the back buffer to the window.
        GAME_WINDOW.fill((0, 0, 0), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        GAME_WINDOW.blit(SCALED_BACK_BUFFER, BACK_BUFFER_DST)

        return True

    def main(self):
        game_running = True
        while game_running:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        game_running = False
                    case (pygame.KEYDOWN | pygame.KEYUP |
                          pygame.JOYBUTTONDOWN | pygame.JOYBUTTONUP |
                          pygame.JOYAXISMOTION | pygame.JOYHATMOTION |
                          pygame.JOYDEVICEADDED | pygame.JOYDEVICEREMOVED):
                        self.input_manager.handle_event(event)

            if not self.update():
                game_running = False

            pygame.display.update()
            self.clock.tick(FRAME_RATE)
        pygame.quit()


game = Game()
game.main()
