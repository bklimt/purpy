
from enum import Enum

import pygame


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

    @classmethod
    def from_str(cls, s: str) -> 'Direction':
        match s:
            case 'N': return Direction.UP
            case 'S': return Direction.DOWN
            case 'W': return Direction.LEFT
            case 'E': return Direction.RIGHT
        raise Exception(f'invalid direction {s}')

    def opposite(self) -> 'Direction':
        match self:
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


def try_move_to_bounds(actor: pygame.Rect, target: pygame.Rect, direction: Direction) -> int:
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
        case Direction.UP:
            return target.bottom - actor.top
        case Direction.DOWN:
            return target.top - actor.bottom
        case Direction.RIGHT:
            return target.left - actor.right
        case Direction.LEFT:
            return target.right - actor.left
    raise Exception('unimplemented')


def try_move_to_slope_bounds(
        actor: pygame.Rect,
        target: pygame.Rect,
        left_y: int,
        right_y: int,
        direction: Direction) -> int:
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

    if direction != Direction.DOWN:
        return 0

    target_y: int = actor.bottom
    actor_center_x = (actor.left + actor.right) // 2

    if actor_center_x < target.left:
        target_y = target.top + left_y
    elif actor_center_x > target.right:
        target_y = target.top + right_y
    else:
        x_offset = actor_center_x - target.x
        slope = (right_y - left_y) / target.w
        target_y = int(target.y + slope * x_offset + left_y)

        if False:
            print(f'center_x = {actor_center_x}')
            print(f'x_offset = {x_offset}')
            print(f'slope = {slope}')
            print(f'target_y = {target_y}')
            print(f'actor_bottom = {actor.bottom}')

    if target_y < actor.bottom:
        return target_y - actor.bottom
    else:
        return 0


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


def inside(rect: pygame.Rect, point: tuple[int, int]) -> bool:
    if point[0] < rect.left or point[0] > rect.right:
        return False
    if point[1] < rect.top or point[1] > rect.bottom:
        return False
    return True
