
import map
import math
import pygame

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
LOGICAL_WIDTH = 640
LOGICAL_HEIGHT = 480
FRAME_RATE = 60

pygame.init()
clock = pygame.time.Clock()

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

MAP = map.load_map('assets/map.tmx')

x = 0
y = 0
dx = 0
dy = 0


def update():
    global x, y
    x = x + dx
    y = y + dy

    pygame.draw.rect(BACK_BUFFER, (0, 0, 0), BACK_BUFFER_SRC)
    MAP.draw(BACK_BUFFER, pygame.Rect(
        0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT), (x, y))

    pygame.draw.rect(GAME_WINDOW, (0, 0, 0),
                     (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.draw.rect(GAME_WINDOW, (255, 255, 255),
                     BACK_BUFFER_DST)

    pygame.transform.scale(
        BACK_BUFFER, SCALED_BACK_BUFFER_SIZE, SCALED_BACK_BUFFER)

    GAME_WINDOW.blit(SCALED_BACK_BUFFER, BACK_BUFFER_DST)


game_running = True
while game_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                dx = 10
            if event.key == pygame.K_d:
                dx = -10
            if event.key == pygame.K_w:
                dy = 10
            if event.key == pygame.K_s:
                dy = -10
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_d:
                dx = 0
            if event.key == pygame.K_w or event.key == pygame.K_s:
                dy = 0
    update()
    pygame.display.update()
    clock.tick(FRAME_RATE)

pygame.quit()
