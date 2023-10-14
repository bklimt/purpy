
from inputmanager import InputManager
from level import Level
import os
import pygame

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
LOGICAL_WIDTH = 320
LOGICAL_HEIGHT = 180
FRAME_RATE = 60

pygame.init()

BACK_BUFFER: pygame.Surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
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
    level: int = 0
    levels: list[str] = []
    clock = pygame.time.Clock()
    input_manager = InputManager()
    scene: Level

    def __init__(self):
        self.levels = sorted(
            [f'assets/levels/{s}' for s in os.listdir('assets/levels') if s.endswith('.tmx')])
        for path in self.levels:
            print(f'level: {path}')
        self.level = 0
        self.scene = Level(self.levels[0])

    def update(self):
        if self.input_manager.is_key_triggered(pygame.K_1):
            self.level = (self.level + 1) % len(self.levels)
            self.scene = Level(self.levels[self.level])

        # Update the actual game logic.
        self.scene.update(self.input_manager)

        # Clear the back buffer with solid black.
        # pygame.draw.rect(BACK_BUFFER, (0, 0, 0), BACK_BUFFER_SRC)
        BACK_BUFFER.fill((0, 0, 0), BACK_BUFFER_SRC)
        # Draw the scene.
        self.scene.draw(BACK_BUFFER, pygame.Rect(
            0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT))
        # Clear the window with black.
        # pygame.draw.rect(GAME_WINDOW, (0, 0, 0),
        #                  (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        GAME_WINDOW.fill((0, 0, 0), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        # Scale the back buffer to the right size.
        pygame.transform.scale(
            BACK_BUFFER, SCALED_BACK_BUFFER_SIZE, SCALED_BACK_BUFFER)
        # Copy the back buffer to the window.
        GAME_WINDOW.blit(SCALED_BACK_BUFFER, BACK_BUFFER_DST)

    def main(self):
        game_running = True
        while game_running:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        game_running = False
                    case (pygame.KEYDOWN | pygame.KEYUP |
                          pygame.JOYBUTTONDOWN | pygame.JOYBUTTONUP |
                          pygame.JOYAXISMOTION | pygame.JOYHATMOTION):
                        self.input_manager.handle_event(event)

            if self.input_manager.is_key_triggered(pygame.K_ESCAPE):
                game_running = False

            self.update()
            pygame.display.update()
            self.clock.tick(FRAME_RATE)
            self.input_manager.update()
        pygame.quit()


game = Game()
game.main()
