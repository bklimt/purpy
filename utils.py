
from enum import Enum
import pygame
import xml.etree.ElementTree


class Direction(Enum):
    NONE = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


def opposite_direction(d: Direction) -> Direction:
    match d:
        case Direction.NONE:
            raise Exception('cannot take the opposite of no direction')
        case Direction.UP:
            return Direction.DOWN
        case Direction.DOWN:
            return Direction.UP
        case Direction.RIGHT:
            return Direction.LEFT
        case Direction.LEFT:
            return Direction.RIGHT


def sign(n: int):
    if n < 0:
        return -1
    if n > 0:
        return 1
    return 0


def cmp_in_direction(a: int, b: int, direction: Direction):
    if direction == Direction.UP or direction == Direction.LEFT:
        return sign(b - a)
    else:
        return sign(a - b)


class Bounds:
    x_sub: int
    y_sub: int
    w_sub: int
    h_sub: int

    def __init__(self, x_sub: int, y_sub: int, w_sub: int, h_sub: int):
        self.x_sub = x_sub
        self.y_sub = y_sub
        self.w_sub = w_sub
        self.h_sub = h_sub

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, self.h)

    @property
    def x(self) -> int:
        return self.x_sub // 16

    @property
    def y(self) -> int:
        return self.y_sub // 16

    @property
    def w(self) -> int:
        return self.w_sub // 16

    @property
    def h(self) -> int:
        return self.h_sub // 16

    @property
    def top(self) -> int:
        return self.y

    @property
    def left(self) -> int:
        return self.x

    @property
    def bottom(self) -> int:
        return self.bottom_sub // 16

    @property
    def right(self) -> int:
        return self.right_sub // 16

    @property
    def top_sub(self) -> int:
        return self.y_sub

    @property
    def left_sub(self) -> int:
        return self.x_sub

    @property
    def right_sub(self) -> int:
        return self.x_sub + self.w_sub

    @property
    def bottom_sub(self) -> int:
        return self.y_sub + self.h_sub

    def __str__(self) -> str:
        return f'Bounds({self.x_sub}, {self.y_sub}, {self.w_sub}, {self.h_sub})'


def try_move_to_bounds(actor: Bounds, target: Bounds, direction: Direction) -> int:
    """Try to move the actor rect in direction by delta and see if it intersects target.

    Returns the maximum distance the actor can move.
    """
    if actor.bottom_sub <= target.top_sub:
        return 0
    if actor.top_sub >= target.bottom_sub:
        return 0
    if actor.right_sub <= target.left_sub:
        return 0
    if actor.left_sub >= target.right_sub:
        return 0

    match direction:
        case Direction.NONE:
            raise Exception('cannot try_move_to in no direction')
        case Direction.UP:
            return target.bottom_sub - actor.top_sub
        case Direction.DOWN:
            return target.top_sub - actor.bottom_sub
        case Direction.RIGHT:
            return target.left_sub - actor.right_sub
        case Direction.LEFT:
            return target.right_sub - actor.left_sub
    raise Exception('unimplemented')


def intersect(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
    if rect1.right < rect2.left:
        return False
    if rect1.left > rect2.right:
        return False
    if rect1.bottom < rect2.top:
        return False
    if rect1.top > rect2.bottom:
        return False
    return True


def load_properties(
        node: xml.etree.ElementTree.Element,
        properties: dict[str, str | int | bool] | None = None
) -> dict[str, str | int | bool]:
    if properties is None:
        properties = {}

    for pnode in node:
        if pnode.tag == 'properties' or pnode.tag == 'property':
            load_properties(pnode, properties)

    if node.tag == 'property':
        name = node.attrib['name']
        typ = node.attrib.get('type', 'str')
        val = node.attrib['value']
        if typ == "str":
            properties[name] = val
        elif typ == "int":
            properties[name] = int(val)
        elif typ == "bool":
            properties[name] = (val == 'true')
        else:
            raise Exception(f'unsupported property type {typ}')

    return properties


def assert_bool(val: bool | int | str) -> bool:
    if not isinstance(val, bool):
        raise Exception(f'expected bool, got {val}')
    return val


def assert_int(val: bool | int | str) -> int:
    if not isinstance(val, int):
        raise Exception(f'expected int, got {val}')
    return val


def assert_str(val: bool | int | str) -> str:
    if not isinstance(val, str):
        raise Exception(f'expected str, got {val}')
    return val
