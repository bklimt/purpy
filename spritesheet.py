
import pygame
import typing

from render.spritebatch import SpriteBatch


class SpriteSheet:
    surface: pygame.Surface
    reverse: pygame.Surface
    sprite_width: int
    sprite_height: int
    columns: int

    def __init__(self, surface: pygame.Surface, sprite_width: int, sprite_height: int):
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.surface = surface
        self.reverse = pygame.transform.flip(surface, True, False)
        self.columns = surface.get_width() // sprite_width

    def sprite(self, index: int, layer: int, reverse: bool) -> pygame.Rect:
        column = index % self.columns
        row = index // self.columns
        if reverse:
            column = (self.columns - 1) - column
        row += layer
        x = column * self.sprite_width
        y = row * self.sprite_height
        return pygame.Rect(x, y, self.sprite_width, self.sprite_height)

    def blit(self,
             batch: SpriteBatch,
             dest: pygame.Rect,
             index: int = 0,
             layer: int = 0,
             reverse: bool = False):
        texture = self.surface
        if reverse:
            texture = self.reverse
        sprite = self.sprite(index, layer, reverse)
        batch.draw(texture, dest, sprite)


class Animation:
    spritesheet: SpriteSheet
    index: int = 0
    frames: int
    frames_per_frame: int = 2
    timer: int

    def __init__(self, surface: pygame.Surface, sprite_width: int, sprite_height: int):
        self.spritesheet = SpriteSheet(surface, sprite_width, sprite_height)
        if surface.get_height() != sprite_height:
            raise Exception('animations can only have one row')
        self.frames = surface.get_width() // sprite_width
        self.timer = self.frames_per_frame

    def update(self):
        if self.timer == 0:
            self.index = (self.index + 1) % self.frames
            self.timer = self.frames_per_frame
        else:
            self.timer -= 1

    def blit(self, batch: SpriteBatch, dest: pygame.Rect, reverse: bool):
        self.spritesheet.blit(batch, dest, self.index, reverse)


class AnimationStateMachineRule:
    current_range: tuple[int, int] | None  # This is an inclusive range.
    current_state: str | None
    next_frame: int | typing.Callable[[int], int]

    def __init__(self, text: str, acceptable_states: set[str]):
        # e.g. 1-2, STATE: +
        text = text.strip()
        parts = text.split(':')
        if len(parts) != 2:
            raise Exception(
                f'invalid animation state machine rule (missing colon): {text}')
        antecedent_text = parts[0].strip()
        consequent_text = parts[1].strip()

        antecedent_parts = antecedent_text.split(',')
        if len(antecedent_parts) != 2:
            raise Exception(
                f'invalid animation state machine rule (missing comma): {text}')
        range_text = antecedent_parts[0].strip()
        current_state_text = antecedent_parts[1].strip()

        if range_text == '*':
            self.current_range = None
        else:
            range_parts = range_text.split('-')
            if len(range_parts) != 2:
                raise Exception(
                    f'invalid animation state machine rule (missing dash): {text}')
            range_start_text = range_parts[0].strip()
            range_end_text = range_parts[1].strip()
            self.current_range = (int(range_start_text), int(range_end_text))

        if current_state_text == '*':
            self.current_state = None
        else:
            if current_state_text not in acceptable_states:
                raise Exception(
                    f'invalid animation state machine rule (invalid state): {text}')
            self.current_state = current_state_text

        if consequent_text == '+':
            self.next_frame = lambda x: x + 1
        elif consequent_text == '-':
            self.next_frame = lambda x: x - 1
        elif consequent_text == '=':
            self.next_frame = lambda x: x
        else:
            self.next_frame = int(consequent_text)

    def matches(self, current_frame: int, current_state: str) -> bool:
        if self.current_range is not None:
            if current_frame < self.current_range[0]:
                return False
            if current_frame > self.current_range[1]:
                return False
        if self.current_state is not None:
            if current_state != self.current_state:
                return False
        return True

    def apply(self, current_frame) -> int:
        if isinstance(self.next_frame, int):
            return self.next_frame
        return self.next_frame(current_frame)


class AnimationStateMachine:
    rules: list[AnimationStateMachineRule]

    def __init__(self, text: str):
        self.rules = []
        states: set[str] = set()
        in_transitions = False
        for line in text.split('\n'):
            line = line.strip()
            if line == '':
                continue
            if line[0] == '#':
                continue
            if line == '[STATES]':
                in_transitions = False
            elif line == '[TRANSITIONS]':
                in_transitions = True
            elif not in_transitions:
                states.add(line)
            else:
                rule = AnimationStateMachineRule(line, states)
                self.rules.append(rule)

    def next_frame(self, current_frame: int, current_state: str) -> int:
        for rule in self.rules:
            if rule.matches(current_frame, current_state):
                return rule.apply(current_frame)
        raise Exception(
            f'unhandled state machine case: {current_frame}, {current_state}')
