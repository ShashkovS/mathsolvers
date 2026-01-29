import unittest
from fractions import Fraction

from mathsolvers.sympy_stuff import patched_rational
from mathsolvers.sympy_stuff import tests_wrapper


class Test(tests_wrapper.TestSolver):
    def test_rat_1(self):
        for p1 in range(-20, -10):
            for q1 in range(1, 11):
                for p2 in range(-20, 21):
                    for q2 in range(1, 11):
                        f1 = Fraction(p1, q1)
                        f2 = Fraction(p2, q2)
                        ff1 = patched_rational._Op_wrapper(p1, q1)
                        ff2 = patched_rational._Op_wrapper(p2, q2)
                        self.assertEqual(f1 + f2, ff1 + ff2, f'{f1=} {f2=}')
                        self.assertEqual(f1 - f2, ff1 - ff2, f'{f1=} {f2=}')
                        self.assertEqual(f1 * f2, ff1 * ff2, f'{f1=} {f2=}')

    def test_rat_2(self):
        for p1 in range(-10, 0):
            for q1 in range(1, 11):
                for p2 in range(-20, 21):
                    for q2 in range(1, 11):
                        f1 = Fraction(p1, q1)
                        f2 = Fraction(p2, q2)
                        ff1 = patched_rational._Op_wrapper(p1, q1)
                        ff2 = patched_rational._Op_wrapper(p2, q2)
                        self.assertEqual(f1 + f2, ff1 + ff2, f'{f1=} {f2=}')
                        self.assertEqual(f1 - f2, ff1 - ff2, f'{f1=} {f2=}')
                        self.assertEqual(f1 * f2, ff1 * ff2, f'{f1=} {f2=}')

    def test_rat_3(self):
        for p1 in range(11):
            for q1 in range(1, 11):
                for p2 in range(-20, 21):
                    for q2 in range(1, 11):
                        f1 = Fraction(p1, q1)
                        f2 = Fraction(p2, q2)
                        ff1 = patched_rational._Op_wrapper(p1, q1)
                        ff2 = patched_rational._Op_wrapper(p2, q2)
                        self.assertEqual(f1 + f2, ff1 + ff2, f'{f1=} {f2=}')
                        self.assertEqual(f1 - f2, ff1 - ff2, f'{f1=} {f2=}')
                        self.assertEqual(f1 * f2, ff1 * ff2, f'{f1=} {f2=}')

    def test_rat_4(self):
        for p1 in range(11, 21):
            for q1 in range(1, 11):
                for p2 in range(-20, 21):
                    for q2 in range(1, 11):
                        f1 = Fraction(p1, q1)
                        f2 = Fraction(p2, q2)
                        ff1 = patched_rational._Op_wrapper(p1, q1)
                        ff2 = patched_rational._Op_wrapper(p2, q2)
                        self.assertEqual(f1 + f2, ff1 + ff2, f'{f1=} {f2=}')
                        self.assertEqual(f1 - f2, ff1 - ff2, f'{f1=} {f2=}')
                        self.assertEqual(f1 * f2, ff1 * ff2, f'{f1=} {f2=}')


if __name__ == '__main__':
    unittest.main()
