
from enum import Enum
import pygame

# TODO: Change these to up down left and right.


class Direction(Enum):
    NONE = 0
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4


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


def try_move_to(actor: pygame.Rect, target: pygame.Rect, direction: Direction) -> int:
    """Try to move the actor rect in direction by delta and see if it intersects target.

    Returns the maximum distance the actor can move.
    """
    if actor.bottom <= target.top:
        return 0
    if actor.top >= target.bottom:
        return 0
    if actor.right <= target.left:
        return 0
    if actor.left >= target.right:
        return 0

    match direction:
        case Direction.NONE:
            raise Exception('cannot try_move_to in no direction')
        case Direction.NORTH:
            return target.bottom - actor.top
        case Direction.SOUTH:
            return target.top - actor.bottom
        case Direction.EAST:
            return target.left - actor.right
        case Direction.WEST:
            return target.right - actor.left
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
