
import pygame
import typing

from enum import Enum


class InputState:
    keys_down: dict[int, bool] = {}
    joystick_buttons_down: dict[int, bool] = {}
    mouse_buttons_down: dict[int, bool] = {}
    mouse_position: tuple[int, int] = (0, 0)
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

    def set_joystick_button_down(self, button: int):
        self.joystick_buttons_down[button] = True

    def set_joystick_button_up(self, button: int):
        self.joystick_buttons_down[button] = False

    def is_joystick_button_down(self, button: int) -> bool:
        return self.joystick_buttons_down.get(button, False)

    def set_mouse_button_down(self, button: int):
        self.mouse_buttons_down[button] = True

    def set_mouse_button_up(self, button: int):
        self.mouse_buttons_down[button] = False

    def is_mouse_button_down(self, button: int) -> bool:
        return self.mouse_buttons_down.get(button, False)


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

    def __init__(self, key: int):
        self.key = key

    def update_on(self, state: InputState) -> bool:
        return state.is_key_down(self.key)


class JoystickButtonInput(CachedBinaryInput):
    """ Returns True as long as a button is down. """
    button: int

    def __init__(self, button: int):
        self.button = button

    def update_on(self, state: InputState) -> bool:
        return state.is_joystick_button_down(self.button)


class MouseButtonInput(CachedBinaryInput):
    """ Returns True as long as a button is down. """
    button: int

    def __init__(self, button: int):
        self.button = button

    def update_on(self, state: InputState) -> bool:
        return state.is_mouse_button_down(self.button)


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
    PLAYER_JUMP_TRIGGER = 6
    PLAYER_JUMP_DOWN = 7
    MENU_DOWN = 8
    MENU_UP = 9
    RESTART = 10
    MOUSE_PRESS = 11


class InputSnapshot:
    ok: bool
    cancel: bool
    player_left: bool
    player_right: bool
    player_crouch: bool
    player_jump_trigger: bool
    player_jump_down: bool
    menu_down: bool
    menu_up: bool

    def __init__(self, encoded=0):
        self.ok = (encoded & (1 << 0)) != 0
        self.cancel = (encoded & (1 << 1)) != 0
        self.player_left = (encoded & (1 << 2)) != 0
        self.player_right = (encoded & (1 << 3)) != 0
        self.player_crouch = (encoded & (1 << 4)) != 0
        self.player_jump_trigger = (encoded & (1 << 5)) != 0
        self.player_jump_down = (encoded & (1 << 6)) != 0
        self.menu_down = (encoded & (1 << 7)) != 0
        self.menu_up = (encoded & (1 << 8)) != 0


class RecorderEntry(typing.NamedTuple):
    frame: int
    snapshot: int


class InputRecorder:
    previous: int
    queue: list[RecorderEntry]

    def __init__(self):
        self.previous = 0
        self.queue = []

    def playback(self, frame: int) -> InputSnapshot:
        if len(self.queue) > 0:
            if self.queue[0].frame == frame:
                self.previous = self.queue[0].snapshot
                self.queue = self.queue[1:]
        return InputSnapshot(self.previous)

    def load(self, path):
        f = open(path)
        text = f.read()
        lines = [line.strip()
                 for line in text.split('\n') if len(line.strip()) != 0]
        for line in lines:
            frame, snapshot = line.split(',')
            frame = int(frame)
            snapshot = int(snapshot)
            self.queue.append(RecorderEntry(frame, snapshot))


class InputManager:
    state: InputState
    binary_hooks: dict[BinaryInput, BinaryInputType]
    playback: bool = False
    recorder: InputRecorder

    def __init__(self, playback_path: str | None):
        pygame.joystick.init()
        self.state = InputState()
        self.state.reset_joystick()

        self.binary_hooks = {
            BinaryInput.OK: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_RETURN)),
                TriggerInput(JoystickButtonInput(0)),
            ]),
            BinaryInput.CANCEL: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_ESCAPE)),
                TriggerInput(KeyInput(pygame.K_1)),
                TriggerInput(JoystickButtonInput(2)),
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
            BinaryInput.PLAYER_JUMP_TRIGGER: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_SPACE)),
                TriggerInput(KeyInput(pygame.K_w)),
                TriggerInput(KeyInput(pygame.K_UP)),
                TriggerInput(JoystickButtonInput(0)),
            ]),
            BinaryInput.PLAYER_JUMP_DOWN: AnyOfInput([
                KeyInput(pygame.K_SPACE),
                KeyInput(pygame.K_w),
                KeyInput(pygame.K_UP),
                JoystickButtonInput(0),
            ]),
            BinaryInput.MENU_DOWN: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_DOWN)),
                TriggerInput(KeyInput(pygame.K_s)),
                TriggerInput(JoystickThresholdInput(1, None, 0.5)),
            ]),
            BinaryInput.MENU_UP: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_UP)),
                TriggerInput(KeyInput(pygame.K_w)),
                TriggerInput(JoystickThresholdInput(1, -0.5, None)),
            ]),
            BinaryInput.RESTART: AnyOfInput([
                TriggerInput(KeyInput(pygame.K_2)),
            ]),
            BinaryInput.MOUSE_PRESS: AnyOfInput([
                TriggerInput(MouseButtonInput(1)),
                TriggerInput(KeyInput(pygame.K_p)),
            ]),
        }

        self.recorder = InputRecorder()
        if playback_path is not None:
            self.playback = True
            self.recorder.load(playback_path)

    def update(self, frame: int) -> InputSnapshot:
        if self.playback:
            return self.recorder.playback(frame)

        for hook in self.binary_hooks.keys():
            self.binary_hooks[hook].update(self.state)
        return self.take_snapshot()

    def take_snapshot(self) -> InputSnapshot:
        snapshot = InputSnapshot()
        snapshot.ok = self.binary_hooks[BinaryInput.OK].is_on()
        snapshot.cancel = self.binary_hooks[BinaryInput.CANCEL].is_on()
        snapshot.player_left = self.binary_hooks[BinaryInput.PLAYER_LEFT].is_on(
        )
        snapshot.player_right = self.binary_hooks[BinaryInput.PLAYER_RIGHT].is_on(
        )
        snapshot.player_crouch = self.binary_hooks[BinaryInput.PLAYER_CROUCH].is_on(
        )
        snapshot.player_jump_trigger = self.binary_hooks[BinaryInput.PLAYER_JUMP_TRIGGER].is_on(
        )
        snapshot.player_jump_down = self.binary_hooks[BinaryInput.PLAYER_JUMP_DOWN].is_on(
        )
        snapshot.menu_down = self.binary_hooks[BinaryInput.MENU_DOWN].is_on()
        snapshot.menu_up = self.binary_hooks[BinaryInput.MENU_UP].is_on()
        return snapshot

    def handle_keyboard_event(self, event: pygame.event.Event):
        match event.type:
            case pygame.KEYDOWN:
                self.state.set_key_down(event.key)
            case pygame.KEYUP:
                self.state.set_key_up(event.key)

    def handle_joystick_event(self, event: pygame.event.Event):
        match event.type:
            case pygame.JOYBUTTONDOWN:
                print(f'button {event.button}')
                self.state.set_joystick_button_down(event.button)
            case pygame.JOYBUTTONUP:
                self.state.set_joystick_button_up(event.button)
            case pygame.JOYDEVICEADDED:
                self.state.reset_joystick()
            case pygame.JOYDEVICEREMOVED:
                self.state.reset_joystick()
            case pygame.JOYAXISMOTION:
                pass
            case pygame.JOYHATMOTION:
                pass

    def handle_mouse_event(self, event: pygame.event.Event):
        match event.type:
            case pygame.MOUSEMOTION:
                print(f'mouse motion {event.pos}')
                self.state.mouse_position = event.pos
            case pygame.MOUSEBUTTONDOWN:
                print(f'mouse button {event.button} down {event.pos}')
                self.state.set_mouse_button_down(event.button)
            case pygame.MOUSEBUTTONUP:
                print(f'mouse button {event.button} up {event.pos}')
                self.state.set_mouse_button_up(event.button)

    @property
    def mouse_position(self) -> tuple[int, int]:
        return self.state.mouse_position

    def is_mouse_pressed(self) -> bool:
        return self.binary_hooks[BinaryInput.MOUSE_PRESS].is_on()
