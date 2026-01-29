import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    r'<<solve 2x = 3 >>',
    r'<<solve 2x + 3y  = 5 \\ x+y=-1 >>',
    r'<<simplify 1 2/3 + 5/6 >>',
    r'<<simplify (1+x)/(2+3x) \\ x=3 >>',
    r'<<simplify (y+x)/(2+3x) \\ x=3 \\ y = -1>>',
    r'<<units 2м 315см >>',
    r'<<units 2м 310см \\ м \\ дм >>',
    r'<<factor 2024 >>',
    r'<<factor x^2 + 2x + 1 >>',
]


class Test(tests_wrapper.TestSolver):
    def test_multiple_calls1(self):
        call1 = '<<solve 2x+1=0>>'
        call2 = '<<simplify x * x * x>>'
        call3 = r'<<units 2м \\ дм>>'
        self.assertDictEqual(mathsolvers.solver(f'{call1}\n{call2}\n{call3}'),
                             mathsolvers.solver([call1, call2, call3]))
        res1 = mathsolvers.solver(call1)
        res2 = mathsolvers.solver(call2)
        res3 = mathsolvers.solver(call3)
        res_global = mathsolvers.solver(call1 + call2 + call3)
        print('res_global', res_global)
        self.assertEqual(
            res_global['final_answer'],
            f"{res1['final_answer']}; {res2['final_answer']}; {res3['final_answer']}",
        )
        self.assertEqual(
            sum(key.startswith('step ') for key in res_global),
            sum(key.startswith('step ') for key in res1) + sum(key.startswith('step ') for key in res2) +
            sum(key.startswith('step ') for key in res3)
        )

    def test_multiple_calls2(self):
        call1 = '<<solve 2x+1=0>>'
        call2 = '<<simplify x * (x * x >>'  # не парсится
        call3 = r'<<units 2м \\ дм>>'
        self.assertDictEqual(
            mathsolvers.solver(f'{call1}\n{call2}\n{call3}'),
            mathsolvers.solver([call1, call2, call3])
        )
        res1 = mathsolvers.solver(call1)
        res3 = mathsolvers.solver(call3)
        res_global = mathsolvers.solver(call1 + call2 + call3)
        print('res_global', res_global)
        self.assertEqual(
            res_global['final_answer'],
            f"{res1['final_answer']}; {res3['final_answer']}",
        )
        self.assertEqual(
            sum(key.startswith('step ') for key in res_global),
            sum(key.startswith('step ') for key in res1) + sum(key.startswith('step ') for key in res3)
        )


def add_test_methods():
    for i, expr in enumerate(cases):
        def test_solver_with_timeout(self, expr=expr):
            res = mathsolvers.solver(expr)
            resa = self.worker.solver(expr)
            # self.add_res(res)
            self.assertIsNotNone(res)
            self.assertDictEqual(res, resa)

        test_solver_with_timeout.__name__ = tests_wrapper.tnesc(
            tests_wrapper.tnesc(f'test_solver_{i + 1:03}: {expr}'))

        setattr(Test, test_solver_with_timeout.__name__, test_solver_with_timeout)


add_test_methods()
if __name__ == '__main__':
    unittest.main()
