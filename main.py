
import input
import level
import tilemap
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

clock = pygame.time.Clock()
scene = level.Level()


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


def update():
    # Update the actual game logic.
    scene.update()

    # Clear the back buffer with solid black.
    pygame.draw.rect(BACK_BUFFER, (0, 0, 0), BACK_BUFFER_SRC)
    # Draw the scene.
    scene.draw(BACK_BUFFER, pygame.Rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT))
    # Clear the window with black.
    pygame.draw.rect(GAME_WINDOW, (0, 0, 0),
                     (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
    # Scale the back buffer to the right size.
    pygame.transform.scale(
        BACK_BUFFER, SCALED_BACK_BUFFER_SIZE, SCALED_BACK_BUFFER)
    # Copy the back buffer to the window.
    GAME_WINDOW.blit(SCALED_BACK_BUFFER, BACK_BUFFER_DST)


game_running = True
while game_running:
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                game_running = False
            case pygame.KEYDOWN | pygame.KEYUP:
                input.handle_event(event)

    update()
    pygame.display.update()
    clock.tick(FRAME_RATE)

pygame.quit()
