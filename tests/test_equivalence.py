import pprint
import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    ('3*x-1 = -2*x-4', '0= 3*x-1 +4 +2x'),
    ('(x + 1)**2 + sin(2*x)', 'x**2 + 1 + 3*x - x - 2*cos(x)*sin(pi + x)'),
    ('x + 1', '1 + x'),
    ('(x + 1)**2 + sin(2*x) + 32*x', 'x**2 + 1 + 3*x - x - 2*cos(x)*sin(pi + x) + 31*x'),
    ('3*x-1 = -2*x-4', '0= 3*x-1 +4 +2x'),
    ('3*x-1 = -2*x-4', '= x'),
    ('3*x-1 = -2*x-4', '2=x=34-2x'),
    ('3*x-1 >= -2*x-4', '0<= 3*x-1 +4 +2x'),
    ('5*x <= -2*x-4', '<= 3*x-1 +4 +2x'),
    ('3*x-1 >= -2*x-4', '-3 <= 5x'),
    ('x > 3', '9 < 3x'),
    ('1 / (v ^ (1 / 3))', r'1/\sqrt[3]{v}'),
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (expr1, expr2) in enumerate(cases):

        def test_template_with_timeout(self, expr1=expr1, expr2=expr2):
            print(f'\n{expr1=} {expr2=}')
            res = mathsolvers.check_equivalence(expr1, expr2)
            resa = self.worker.check_equivalence(expr1, expr2, timeout=3)
            pprint.pprint(res, width=120, compact=False, sort_dicts=False)
            self.assertIsNotNone(res)
            self.assertDictEqual(res, resa)

        test_template_with_timeout.__name__ = tests_wrapper.tnesc(
            f'test_check_equivalence_{i + 1:03}: {expr1} == {expr2}'
        )

        setattr(Test, test_template_with_timeout.__name__, test_template_with_timeout)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
