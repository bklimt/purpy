
import pygame
import unittest

from utils import cmp_in_direction, try_move_to, Direction


class TestIntersect(unittest.TestCase):

    def test_no_intersect(self):
        r1 = pygame.Rect(10, 10, 10, 10)
        r2 = pygame.Rect(20, 20, 10, 10)
        self.assertEqual(0, try_move_to(r1, r2, Direction.EAST))

    def test_simple_intersect(self):
        r1 = pygame.Rect(10, 10, 10, 10)
        r2 = pygame.Rect(18, 10, 10, 10)
        self.assertEqual(-2, try_move_to(r1, r2, Direction.EAST))

    def test_moving_right_intersects_top(self) -> None:
        r1 = pygame.Rect(10, 10, 10, 10)
        r2 = pygame.Rect(12, 6, 5, 10)
        self.assertEqual(-8, try_move_to(r1, r2, Direction.EAST))

    def test_moving_already_past(self):
        target = pygame.Rect(10, 0, 5, 5)
        actor = pygame.Rect(0, 0, 5, 5)
        self.assertEqual(0, try_move_to(actor, target, Direction.EAST))

    def test_moving_up(self):
        actor = pygame.Rect(16, 150, 8, 19)
        target = pygame.Rect(16, 168, 8, 8)
        self.assertEqual(26, try_move_to(actor, target, Direction.NORTH))

    def test_cmp_in_direction_right(self):
        self.assertEqual(-1, cmp_in_direction(-8, 0, Direction.EAST))
        self.assertEqual(1, cmp_in_direction(0, -8, Direction.EAST))

    def test_cmp_in_direction_down(self):
        self.assertEqual(-1, cmp_in_direction(-8, 0, Direction.SOUTH))
        self.assertEqual(1, cmp_in_direction(0, -8, Direction.SOUTH))


if __name__ == '__main__':
    unittest.main()
