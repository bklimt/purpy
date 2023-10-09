
import pygame

keys_down: dict[int, bool] = {}


def handle_event(event: pygame.event.Event):
    match event.type:
        case pygame.KEYDOWN:
            keys_down[event.key] = True
        case pygame.KEYUP:
            keys_down[event.key] = False


def is_key_down(key: int) -> bool:
    return keys_down.get(key, False)
