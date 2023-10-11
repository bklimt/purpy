
import pygame


class InputManager:
    keys_down: dict[int, bool] = {}

    def __init__(self):
        pass

    def handle_event(self, event: pygame.event.Event):
        match event.type:
            case pygame.KEYDOWN:
                self.keys_down[event.key] = True
            case pygame.KEYUP:
                self.keys_down[event.key] = False

    def is_key_down(self, key: int) -> bool:
        return self.keys_down.get(key, False)

    def is_left_down(self) -> bool:
        return self.is_key_down(pygame.K_LEFT) or self.is_key_down(pygame.K_a)

    def is_right_down(self) -> bool:
        return self.is_key_down(pygame.K_RIGHT) or self.is_key_down(pygame.K_d)

    def is_jump_down(self) -> bool:
        return self.is_key_down(pygame.K_SPACE) or self.is_key_down(pygame.K_w)
