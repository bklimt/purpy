
from enum import Enum
import pygame


class Direction(Enum):
    NONE = 0
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4


class Intersection:
    """ A single instance of a sprite intersecting a target. """
    direction: Direction
    result: pygame.Rect

    def __init__(self, direction: Direction, result: pygame.Rect):
        self.direction = direction
        self.result = result


class IntersectionList:
    """ A sorted list of intersections. """
    intersections: list[Intersection]

    def __init__(self):
        self.intersections = []

    def add(self, intersection: Intersection):
        self.intersections.append(intersection)


def compute_intersection_right(actor: pygame.Rect, target: pygame.Rect) -> Intersection | None:
    if actor.right > target.left:
        rect = pygame.Rect(target.left - actor.w, actor.top, actor.w, actor.h)
        return Intersection(Direction.EAST, rect)
    return None


def compute_intersection_left(actor: pygame.Rect, target: pygame.Rect) -> Intersection | None:
    if actor.left < target.right:
        rect = pygame.Rect(target.right, actor.top, actor.w, actor.h)
        return Intersection(Direction.WEST, rect)
    return None


def compute_intersection_down(actor: pygame.Rect, target: pygame.Rect) -> Intersection | None:
    if actor.bottom > target.top:
        rect = pygame.Rect(actor.left,
                           target.top - actor.h,
                           actor.w, actor.h)
        return Intersection(Direction.SOUTH, rect)
    return None


def compute_intersection_up(actor: pygame.Rect, target: pygame.Rect) -> Intersection | None:
    if actor.top < target.bottom:
        rect = pygame.Rect(actor.left,
                           target.bottom,
                           actor.w, actor.h)
        return Intersection(Direction.NORTH, rect)
    return None


def compute_intersection(actor: pygame.Rect, target: pygame.Rect, direction: Direction) -> Intersection | None:
    match direction:
        case Direction.NONE:
            raise Exception('cannot compute intersection when not moving')
        case Direction.NORTH:
            return compute_intersection_up(actor, target)
        case Direction.SOUTH:
            return compute_intersection_down(actor, target)
        case Direction.EAST:
            return compute_intersection_right(actor, target)
        case Direction.WEST:
            return compute_intersection_left(actor, target)
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
