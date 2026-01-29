import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    ('2x+y=3', 'x-y=1'),
    ('x+y+z = 1', 'x-y-z = 3', 'y+2z=17'),
    ('x**2 + y - 2*z', 'y + 4*z'),
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, expr in enumerate(cases):

        def test_solve_lin_sys_with_timeout(self, expr=expr):
            res = mathsolvers.solve_lin_sys(*expr)
            # self.add_res(res)
            self.assertIsNotNone(res)

        test_solve_lin_sys_with_timeout.__name__ = tests_wrapper.tnesc(f'test_solve_lin_sys_{i + 1:03}: {expr}')

        setattr(Test, test_solve_lin_sys_with_timeout.__name__, test_solve_lin_sys_with_timeout)


add_test_methods()
if __name__ == '__main__':
    unittest.main()
