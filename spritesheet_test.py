
import unittest

from spritesheet import AnimationStateMachine, AnimationStateMachineRule


class TestRules(unittest.TestCase):
    def test_basic(self):
        rule = AnimationStateMachineRule('1-2, START: 3', set(['START']))
        self.assertTrue(rule.matches(1, 'START'))
        self.assertTrue(rule.matches(2, 'START'))
        self.assertFalse(rule.matches(3, 'START'))
        self.assertFalse(rule.matches(1, 'END'))
        self.assertEqual(3, rule.apply(1))

    def test_range_of_one(self):
        rule = AnimationStateMachineRule('1, START: 3', set(['START']))
        self.assertTrue(rule.matches(1, 'START'))
        self.assertFalse(rule.matches(2, 'START'))
        self.assertFalse(rule.matches(3, 'START'))
        self.assertFalse(rule.matches(1, 'END'))
        self.assertEqual(3, rule.apply(1))

    def test_wildcard_range(self):
        rule = AnimationStateMachineRule('*, START: 3', set(['START']))
        self.assertTrue(rule.matches(1, 'START'))
        self.assertTrue(rule.matches(2, 'START'))
        self.assertTrue(rule.matches(3, 'START'))
        self.assertFalse(rule.matches(1, 'END'))
        self.assertEqual(3, rule.apply(1))

    def test_wildcard_state(self):
        rule = AnimationStateMachineRule('1-2, *: 3', set(['START']))
        self.assertTrue(rule.matches(1, 'START'))
        self.assertTrue(rule.matches(2, 'START'))
        self.assertFalse(rule.matches(3, 'START'))
        self.assertTrue(rule.matches(1, 'END'))
        self.assertEqual(3, rule.apply(1))

    def test_plus(self):
        rule = AnimationStateMachineRule('1-5, START: +', set(['START']))
        self.assertEqual(4, rule.apply(3))

    def test_minus(self):
        rule = AnimationStateMachineRule('1-5, START: -', set(['START']))
        self.assertEqual(2, rule.apply(3))

    def test_equal(self):
        rule = AnimationStateMachineRule('1-5, START: =', set(['START']))
        self.assertEqual(3, rule.apply(3))


TEST_MACHINE_TEXT = """
# Comment

[STATES]
START
END

[TRANSITIONS]
1, START: +
2, START: 1
1-1, END: 2
2-2, END: 3
3-3, END: 3
3-3, START: 1
"""


class TestMachine(unittest.TestCase):
    def test_basic(self):
        machine = AnimationStateMachine(TEST_MACHINE_TEXT)
        self.assertEqual(2, machine.next_frame(1, 'START'))
        self.assertEqual(1, machine.next_frame(2, 'START'))
        self.assertEqual(3, machine.next_frame(2, 'END'))


if __name__ == '__main__':
    unittest.main()
