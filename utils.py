
from enum import Enum
import pygame

# TODO: Change these to up down left and right.


class Direction(Enum):
    NONE = 0
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4


def opposite_direction(d: Direction) -> Direction:
    match d:
        case Direction.NONE:
            raise Exception('cannot take the opposite of no direction')
        case Direction.NORTH:
            return Direction.SOUTH
        case Direction.SOUTH:
            return Direction.NORTH
        case Direction.EAST:
            return Direction.WEST
        case Direction.WEST:
            return Direction.EAST


def sign(n: int):
    if n < 0:
        return -1
    if n > 0:
        return 1
    return 0


def cmp_in_direction(a: int, b: int, direction: Direction):
    if direction == Direction.NORTH or direction == Direction.WEST:
        return sign(b - a)
    else:
        return sign(a - b)


class Bounds:
    x_sub: int
    y_sub: int
    w_sub: int
    h_sub: int

    def __init__(self, x_sub, y_sub, w_sub, h_sub):
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
        case Direction.NORTH:
            return target.bottom_sub - actor.top_sub
        case Direction.SOUTH:
            return target.top_sub - actor.bottom_sub
        case Direction.EAST:
            return target.left_sub - actor.right_sub
        case Direction.WEST:
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
