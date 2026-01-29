import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    (r'<<format 13\% \\ frac>>', r''),
    (r'<<format 1\% \\ frac>>', r''),
    (r'<<format 1 \frac{4}{6} + 2 5/2 \\ frac>>', r''),
    (r'<<format 2\% + 3\% \\ dec>>', r''),
    (r'<<format \frac{1}{2} \\ dec>>', r''),
    (r'<<format \frac{1}{2} + \frac14 \\ dec>>', r''),
    (r'<<format 0,5 \\ frac>>', r''),
    (r'<<format 0,5 + 2 * 3/4 \\ frac>>', r''),
    (r'<<format 0,(3) \\ frac>>', r''),
    (r'<<format 0,(3) + 0,(3) \\ frac>>', r''),
    (r'<<format \frac{1}{3} \\ dec>>', r''),
    (r'<<format 1 + 1\frac{1}{30} \\ dec>>', r''),
    (r'<<format \frac{10}{6} \\ mix>>', r''),
    (r'<<format \frac{10}{6} + 5/3 \\ mix>>', r''),
    (r'<<format 1 \frac{4}{6} \\ frac>>', r''),
    (r'<<format 1 \frac{4}{6} + 2 5/2 \\ frac>>', r''),
    (r'<<format 0,5 \\ perc>>', r''),
    (r'<<format 0,5 + 0,1 \\ perc>>', r''),
    (r'<<format 50\% \\ frac>>', r''),
    (r'<<format 50\% + 15 % \\ frac>>', r''),
    (r'<<format 50\% \\ dec>>', r''),
    (r'<<format 50\% + 15 % \\ dec>>', r''),
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (expr, ans) in enumerate(cases):

        def test_format(self, expr=expr, ans=ans):
            res = mathsolvers.solver(expr)
            self.assertIsNotNone(res)
            if ans:
                final = res.get('final_answer', '').strip(' $')
                are_equal = ans.strip(' $') == final
                if not are_equal:
                    equiv = mathsolvers.check_equivalence(ans, final)
                    are_equal = equiv.get('are_equal', False)
                self.assertTrue(are_equal, f'\n{expr} -> (corr) {ans} ≠ {final} (api)')

        test_format.__name__ = tests_wrapper.tnesc(f'test_format_{i + 1:03}: {expr}')

        setattr(Test, test_format.__name__, test_format)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
