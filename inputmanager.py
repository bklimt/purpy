
import pygame
import typing

from enum import Enum


class InputState:
    keys_down: dict[int, bool] = {}
    buttons_down: dict[int, bool] = {}
    joystick: pygame.joystick.JoystickType | None

    def reset_joystick(self):
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)

    def set_key_down(self, key: int):
        self.keys_down[key] = True

    def set_key_up(self, key: int):
        self.keys_down[key] = False

    def is_key_down(self, key: int) -> bool:
        return self.keys_down.get(key, False)

    def set_button_down(self, button: int):
        self.buttons_down[button] = True

    def set_button_up(self, button: int):
        self.buttons_down[button] = False

    def is_button_down(self, button: int) -> bool:
        return self.buttons_down.get(button, False)


class BinaryInputType(typing.Protocol):
    def update(self, state: InputState) -> None:
        raise Exception('unimplemented')

    def is_on(self) -> bool:
        raise Exception('unimplemented')


class CachedBinaryInput:
    on: bool = False

    def update_on(self, state: InputState) -> bool:
        raise Exception('unimplemented')

    def update(self, state: InputState):
        self.on = self.update_on(state)

    def is_on(self) -> bool:
        return self.on


class KeyInput(CachedBinaryInput):
    """ Returns True as long as a key is down. """
    key: int

    def __init__(self, key):
        self.key = key

    def update_on(self, state: InputState) -> bool:
        return state.is_key_down(self.key)


class ButtonInput(CachedBinaryInput):
    """ Returns True as long as a button is down. """
    button: int

    def __init__(self, button):
        self.button = button

    def update_on(self, state: InputState) -> bool:
        return state.is_button_down(self.button)


class JoystickThresholdInput(CachedBinaryInput):
    axis: int
    low_threshold: float | None
    high_threshold: float | None

    def __init__(self, axis: int, low_threshold: float | None, high_threshold: float | None):
        self.axis = axis
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def get_hat(self, state: InputState) -> float | None:
        if state.joystick is None:
            return None
        if state.joystick.get_numhats() < 1:
            return None
        hat = state.joystick.get_hat(0)
        value = hat[self.axis]
        if self.axis == 1:
            value *= -1
        return value

    def get_axis(self, state: InputState) -> float | None:
        if state.joystick is None:
            return None
        if state.joystick.get_numaxes() < 2:
            return None
        return state.joystick.get_axis(self.axis)

    def update_on(self, state: InputState) -> bool:
        hat = self.get_hat(state)
        if hat is not None:
            if self.low_threshold is not None and hat < self.low_threshold:
                return True
            if self.high_threshold is not None and hat > self.high_threshold:
                return True
        axis = self.get_axis(state)
        if axis is not None:
            if self.low_threshold is not None and axis < self.low_threshold:
                return True
            if self.high_threshold is not None and axis > self.high_threshold:
                return True
        return False


class TriggerInput(CachedBinaryInput):
    """ Wraps a BinaryInput and only returns True once per press. """
    base: CachedBinaryInput
    already_pressed: bool = False

    def __init__(self, base: CachedBinaryInput):
        self.base = base

    def update_on(self, state: InputState) -> bool:
        if self.base.update_on(state):
            if not self.already_pressed:
                self.already_pressed = True
                return True
        else:
            self.already_pressed = False
        return False


class AnyOfInput(BinaryInputType):
    """ Returns True if any of multiple inputs return True. """
    children: typing.Sequence[BinaryInputType]

    def __init__(self, children: typing.Sequence[BinaryInputType]):
        self.children = children

    def update(self, state: InputState):
        for child in self.children:
            child.update(state)

    def is_on(self) -> bool:
        for child in self.children:
            if child.is_on():
                return True
        return False


class BinaryInput(Enum):
    OK = 1
    CANCEL = 2
    PLAYER_LEFT = 3
    PLAYER_RIGHT = 4
    PLAYER_CROUCH = 5
    PLAYER_JUMP = 6
    MENU_DOWN = 7
    MENU_UP = 8
    RESTART = 9


class InputManager:
    state: InputState
    binary_hooks: dict[BinaryInput, BinaryInputType]

    def __init__(self):
        pygame.joystick.init()
        self.state = InputState()
        self.state.reset_joystick()

        self.binary_hooks = {
            BinaryInput.OK: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_RETURN)),
                TriggerInput(ButtonInput(0)),
            ]),
            BinaryInput.CANCEL: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_ESCAPE)),
                TriggerInput(KeyInput(pygame.K_1)),
                TriggerInput(ButtonInput(2)),
            ]),
            BinaryInput.PLAYER_LEFT: AnyOfInput([
                KeyInput(pygame.K_LEFT),
                KeyInput(pygame.K_a),
                JoystickThresholdInput(0, -0.5, None),
            ]),
            BinaryInput.PLAYER_RIGHT: AnyOfInput([
                KeyInput(pygame.K_RIGHT),
                KeyInput(pygame.K_d),
                JoystickThresholdInput(0, None, 0.5),
            ]),
            BinaryInput.PLAYER_CROUCH: AnyOfInput([
                KeyInput(pygame.K_DOWN),
                KeyInput(pygame.K_s),
                JoystickThresholdInput(1, None, 0.5),
            ]),
            BinaryInput.PLAYER_JUMP: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_SPACE)),
                TriggerInput(KeyInput(pygame.K_w)),
                TriggerInput(ButtonInput(0)),
            ]),
            BinaryInput.MENU_DOWN: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_DOWN)),
                TriggerInput(KeyInput(pygame.K_s)),
                TriggerInput(JoystickThresholdInput(1, None, 0.5)),
            ]),
            BinaryInput.MENU_UP: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_UP)),
                TriggerInput(KeyInput(pygame.K_s)),
                TriggerInput(JoystickThresholdInput(1, -0.5, None)),
            ]),
            BinaryInput.RESTART: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_2)),
            ]),
        }

    def update(self):
        for hook in self.binary_hooks.keys():
            self.binary_hooks[hook].update(self.state)

    def handle_event(self, event: pygame.event.Event):
        match event.type:
            case pygame.KEYDOWN:
                self.state.set_key_down(event.key)
            case pygame.KEYUP:
                self.state.set_key_up(event.key)
            case pygame.JOYBUTTONDOWN:
                print(f'button {event.button}')
                self.state.set_button_down(event.button)
            case pygame.JOYBUTTONUP:
                self.state.set_button_up(event.button)
            case pygame.JOYDEVICEADDED:
                self.state.reset_joystick()
            case pygame.JOYDEVICEREMOVED:
                self.state.reset_joystick()
            case pygame.JOYAXISMOTION:
                pass
            case pygame.JOYHATMOTION:
                pass

    def is_ok_triggered(self) -> bool:
        return self.binary_hooks[BinaryInput.OK].is_on()

    def is_cancel_triggered(self) -> bool:
        return self.binary_hooks[BinaryInput.CANCEL].is_on()

    def is_left_down(self) -> bool:
        return self.binary_hooks[BinaryInput.PLAYER_LEFT].is_on()

    def is_right_down(self) -> bool:
        return self.binary_hooks[BinaryInput.PLAYER_RIGHT].is_on()

    def is_jump_down(self) -> bool:
        return self.binary_hooks[BinaryInput.PLAYER_JUMP].is_on()

    def is_crouch_down(self) -> bool:
        return self.binary_hooks[BinaryInput.PLAYER_CROUCH].is_on()

    def is_down_triggered(self) -> bool:
        return self.binary_hooks[BinaryInput.MENU_DOWN].is_on()

    def is_up_triggered(self) -> bool:
        return self.binary_hooks[BinaryInput.MENU_UP].is_on()

    def is_restart_down(self) -> bool:
        return self.binary_hooks[BinaryInput.RESTART].is_on()
