
from utils import assert_int, Bounds, Direction


class Slope:
    left_y: int
    right_y: int

    def __init__(self, properties: dict[str, str | int | bool]):
        self.left_y = assert_int(properties.get('left_y', 0))
        self.right_y = assert_int(properties.get('right_y', 0))

    @property
    def left_y_sub(self):
        return self.left_y * 16

    @property
    def right_y_sub(self):
        return self.right_y * 16

    def try_move_to_bounds(
            self,
            actor: Bounds,
            target: Bounds,
            direction: Direction) -> int:
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

        if direction != Direction.DOWN:
            return 0

        target_y_sub: int = actor.bottom_sub
        actor_center_x_sub = (actor.left_sub + actor.right_sub) // 2

        if actor_center_x_sub < target.left_sub:
            target_y_sub = target.top_sub + self.left_y_sub
        elif actor_center_x_sub > target.right_sub:
            target_y_sub = target.top_sub + self.right_y_sub
        else:
            x_sub_offset = actor_center_x_sub - target.x_sub
            slope_sub = (self.right_y_sub - self.left_y_sub) / target.w_sub
            target_y_sub = int(target.y_sub + slope_sub *
                               x_sub_offset + self.left_y_sub)

            if False:
                print(f'center_x = {actor_center_x_sub}')
                print(f'x_offset = {x_sub_offset}')
                print(f'slope = {slope_sub}')
                print(f'target_y_sub = {target_y_sub}')
                print(f'actor_bottom = {actor.bottom_sub}')

        if target_y_sub < actor.bottom_sub:
            return target_y_sub - actor.bottom_sub
        else:
            return 0
