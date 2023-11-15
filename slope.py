
import pygame

from utils import assert_int, Direction


class Slope:
    left_y: int
    right_y: int

    def __init__(self, properties: dict[str, str | int | bool]):
        self.left_y = assert_int(properties.get('left_y', 0))
        self.right_y = assert_int(properties.get('right_y', 0))

    def try_move_to_bounds(
            self,
            actor: pygame.Rect,
            target: pygame.Rect,
            subpixels: int,
            direction: Direction) -> int:
        """Try to move the actor rect in direction by delta and see if it intersects target.

        Returns the maximum distance the actor can move.
        """
        left_y = self.left_y * subpixels
        right_y = self.right_y * subpixels

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
                print(f'target_y_sub = {target_y}')
                print(f'actor_bottom = {actor.bottom}')

        if target_y < actor.bottom:
            return target_y - actor.bottom
        else:
            return 0
