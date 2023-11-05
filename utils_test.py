
import pygame
import unittest

from utils import cmp_in_direction, try_move_to_bounds, try_move_to_slope_bounds, Bounds, Direction


class TestIntersect(unittest.TestCase):

    def test_no_intersect(self):
        r1 = Bounds(10, 10, 10, 10)
        r2 = Bounds(20, 20, 10, 10)
        self.assertEqual(0, try_move_to_bounds(r1, r2, Direction.RIGHT))

    def test_simple_intersect(self):
        r1 = Bounds(10, 10, 10, 10)
        r2 = Bounds(18, 10, 10, 10)
        self.assertEqual(-2, try_move_to_bounds(r1, r2, Direction.RIGHT))

    def test_moving_right_intersects_top(self) -> None:
        r1 = Bounds(10, 10, 10, 10)
        r2 = Bounds(12, 6, 5, 10)
        self.assertEqual(-8, try_move_to_bounds(r1, r2, Direction.RIGHT))

    def test_moving_already_past(self):
        target = Bounds(10, 0, 5, 5)
        actor = Bounds(0, 0, 5, 5)
        self.assertEqual(0, try_move_to_bounds(actor, target, Direction.RIGHT))

    def test_moving_up(self):
        actor = Bounds(16, 150, 8, 19)
        target = Bounds(16, 168, 8, 8)
        self.assertEqual(26, try_move_to_bounds(
            actor, target, Direction.UP))

    def test_cmp_in_direction_right(self):
        self.assertEqual(-1, cmp_in_direction(-8, 0, Direction.RIGHT))
        self.assertEqual(1, cmp_in_direction(0, -8, Direction.RIGHT))

    def test_cmp_in_direction_down(self):
        self.assertEqual(-1, cmp_in_direction(-8, 0, Direction.DOWN))
        self.assertEqual(1, cmp_in_direction(0, -8, Direction.DOWN))

    def test_slope_down_right(self):
        # The tile is at 40, 80 pixels, which is at 640, 1280 sub-pixels.
        # The tile is 128 sub-pixels in each dimension.
        tile = Bounds(40*16, 80*16, 8*16, 8*16)

        # The player is 24 pixels (384 sub-pixels) wide.
        # and the center x should be 3 pixels (48 sub-pixels) into the tile.
        # The player is at the very top of the tile.
        center_x = 640 + 48
        player = Bounds(center_x - 142, tile.top_sub - 384 + 1, 24*16, 24*16)
        self.assertEqual(897, player.top_sub)
        self.assertEqual(1281, player.bottom_sub)

        # The slope goes from the top of the tile to the middle.
        left_y = 0
        right_y = 3

        result = try_move_to_slope_bounds(
            player, tile, left_y, right_y, Direction.DOWN)
        self.assertEqual(0, result)

        # Now try with the player at the bottom of the tile.
        player.y_sub = tile.bottom_sub - 384 - 1
        result = try_move_to_slope_bounds(
            player, tile, left_y, right_y, Direction.DOWN)
        self.assertEqual(-91, result)


if __name__ == '__main__':
    unittest.main()
