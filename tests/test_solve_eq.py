import pprint
import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    '2x+3=7 2/3',
    ' $3 x^{2}-4 x-20=0$',
    'x +1 = a',
    'x=1',
    '2x=3x',
    '1+x+2=2x+3+5x',
    '4x = 5 2/3',
    r'\frac{1}{4}*x + 2 = 3',
    r'1 + \frac{1}{4}*x - \frac{1}{2} = 2 * (x - \frac{3}{4})',
    '2+2 = x+1-1',
    'X + 3,5 * X = 6,75',
    '0,05 * Х + 0,06 * (50000 - Х) = 2800',
    '0,7 * Х + 0,6 * Х - Х = 18',
    '(7 * Х + Х + (Х + 9)) / 3 = 24,3',
    '5,9999999999999 = x',
    '$\\frac{4}{9}$ * X + 0,8 * X + X = 101',
    'X + 120 * 0,01 * X + $\\frac{4}{5}$ * X = 270',
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, expr in enumerate(cases):

        def test_solve_eq_with_timeout(self, expr=expr):
            res = mathsolvers.solve_eq(expr)
            resa = self.worker.solve_eq(expr, timeout=5)
            pprint.pprint(res, width=120, compact=False, sort_dicts=False)
            self.assertIsNotNone(res)
            self.assertDictEqual(res, resa)

        test_solve_eq_with_timeout.__name__ = tests_wrapper.tnesc(f'test_solve_eq_{i + 1:03}: {expr}')

        setattr(Test, test_solve_eq_with_timeout.__name__, test_solve_eq_with_timeout)


add_test_methods()
if __name__ == '__main__':
    unittest.main()
