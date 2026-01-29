import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    (r'4', r'$4 = 2 \cdot 2$'),
    (r'2024', r'$2024 = 2 \cdot 2 \cdot 2 \cdot 11 \cdot 23$'),
    (r'1', r'$1 = 1$'),
    (r'x', r'$x = x$'),
    (r'x^2 + 2x + 1', r'$x^{2} + 2 x + 1 = (x + 1)^{2}$'),
    (
        r'- 3 a^{2} - 5 a b + 2 b^{2}',
        r'$-3 a^{2} - 5 a b + 2 b^{2} = - (a + 2 b) (3 a - b)$',
    ),  # TODO с минусом некрасиво
    (r'5 + 2 * sqrt(6)', r'$5 + 2 \sqrt{6} = (\sqrt{2} + \sqrt{3})^{2}$'),
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (expr, ans) in enumerate(cases):

        def test_solve_eq_with_timeout(self, expr=expr, ans=ans):
            res = mathsolvers.factor(expr)
            resa = self.worker.factor(expr)
            self.assertIsNotNone(res)
            self.assertDictEqual(res, resa)
            self.assertEqual(res['final_answer'], ans)

        test_solve_eq_with_timeout.__name__ = tests_wrapper.tnesc(f'test_solve_eq_{i + 1:03}: {expr}')

        setattr(Test, test_solve_eq_with_timeout.__name__, test_solve_eq_with_timeout)


add_test_methods()
if __name__ == '__main__':
    unittest.main()
