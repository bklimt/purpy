
import pygame


class InputManager:
    keys_down: dict[int, bool] = {}
    buttons_down: dict[int, bool] = {}
    joystick: pygame.joystick.JoystickType | None

    def __init__(self):
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)

    def handle_event(self, event: pygame.event.Event):
        match event.type:
            case pygame.KEYDOWN:
                self.keys_down[event.key] = True
            case pygame.KEYUP:
                self.keys_down[event.key] = False
            case pygame.JOYBUTTONDOWN:
                print(f'button {event.button}')
                self.buttons_down[event.button] = True
            case pygame.JOYBUTTONUP:
                self.buttons_down[event.button] = False
            case pygame.JOYAXISMOTION:
                pass
            case pygame.JOYHATMOTION:
                pass

    def is_key_down(self, key: int) -> bool:
        return self.keys_down.get(key, False)

    def is_button_down(self, button: int) -> bool:
        return self.buttons_down.get(button, False)

    def get_hat(self) -> tuple[float, float] | None:
        if self.joystick is None:
            return None
        if self.joystick.get_numhats() < 1:
            return None
        return self.joystick.get_hat(0)

    def get_axis(self) -> tuple[float, float] | None:
        if self.joystick is None:
            return None
        if self.joystick.get_numaxes() < 2:
            return None
        return (self.joystick.get_axis(0), self.joystick.get_axis(1))

    def is_left_down(self) -> bool:
        hat = self.get_hat()
        if hat is not None and hat[0] < -0.5:
            return True
        axis = self.get_axis()
        if axis is not None and axis[0] < -0.5:
            return True
        return self.is_key_down(pygame.K_LEFT) or self.is_key_down(pygame.K_a)

    def is_right_down(self) -> bool:
        hat = self.get_hat()
        if hat is not None and hat[0] > 0.5:
            return True
        axis = self.get_axis()
        if axis is not None and axis[0] > 0.5:
            return True
        return self.is_key_down(pygame.K_RIGHT) or self.is_key_down(pygame.K_d)

    def is_jump_down(self) -> bool:
        return self.is_key_down(pygame.K_SPACE) or self.is_key_down(pygame.K_w) or self.is_button_down(0)

    def is_crouch_down(self) -> bool:
        hat = self.get_hat()
        if hat is not None and hat[1] < -0.5:
            return True
        axis = self.get_axis()
        if axis is not None and axis[1] > 0.5:
            return True
        return self.is_key_down(pygame.K_DOWN) or self.is_key_down(pygame.K_s)
