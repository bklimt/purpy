
import pygame
import unittest

from utils import compute_intersection, Direction


class TestIntersect(unittest.TestCase):

    def test_no_intersect(self):
        r1 = pygame.Rect(10, 10, 10, 10)
        r2 = pygame.Rect(20, 20, 10, 10)
        self.assertIsNone(compute_intersection(r1, r2, Direction.EAST))

    def test_simple_intersect(self):
        r1 = pygame.Rect(10, 10, 10, 10)
        r2 = pygame.Rect(18, 10, 10, 10)
        intersection = compute_intersection(r1, r2, Direction.EAST)
        self.assertIsNotNone(intersection)
        assert intersection is not None
        self.assertEqual(8, intersection.result.left)
        self.assertEqual(10, intersection.result.top)
        self.assertEqual(10, intersection.result.w)
        self.assertEqual(10, intersection.result.h)

    def test_moving_right_intersects_top(self) -> None:
        r1 = pygame.Rect(10, 10, 10, 10)
        r2 = pygame.Rect(12, 6, 5, 10)
        intersection = compute_intersection(r1, r2, Direction.EAST)
        self.assertIsNotNone(intersection)
        assert intersection is not None
        self.assertEqual(2, intersection.result.left)
        self.assertEqual(10, intersection.result.top)
        self.assertEqual(10, intersection.result.w)
        self.assertEqual(10, intersection.result.h)

# Map test cases:
# * Moving right intersect a block at the top.
# * Moving right multiple tiles.
# * Intersecting a star and a tile.
# * Moving right and intersecting a tile to the right *and* above.


if __name__ == '__main__':
    unittest.main()
