import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    (r'2x + 2 = 2 - 3x', r'x = 0'),
    (r'2x + 2 = 2 + 3x', r'x = 0'),
    (r'x-2=3', r'x = 5'),
    (r'x+2 = 3', r'x = 1'),
    (r'x + 0.123456789 = 0.123456709', r'x = -8e-8'),
    (r'x + 1/179 = 2/359 + 0.01', r'x = 64161/6426100'),
    (r'x + 1/179 = 2/359', r'x = -1/64261'),
    (r'x + 1/10 = 2', r'x = 19/10'),
    (r'x + 0.1 = 2', r'x = 1,9'),
    (r'X + 120 * 0,01 * X + $\frac{4}{5}$ * X = 270', r'X = 90'),
    (r'$\frac{4}{9}$ * X + 0,8 * X + X = 101', r'X = 45'),
    (r'5,9999999999999 = x', r'x = 5,9999999999999'),
    (r'(7 * x + x + (x + 9)) / 3 = 24,3', r'x = 71/10'),
    (r'0,7 * x + 0,6 * x - x = 18', r'x = 60'),
    (r'0,05 * x + 0,06 * (50000 - x) = 2800', r''),
    (r'X + 3,5 * X = 6,75', r''),
    (r'2+2 = x+1-1', r''),
    (r'1 + \frac{1}{4}*x - \frac{1}{2} = 2 * (x - \frac{3}{4})', r''),
    (r'\frac{1}{4}*x + 2 = 3', r''),
    (r'4x = 5 2/3', r''),
    (r'1+x+2=2x+3+5x', r''),
    (r'2x=3x', r''),
    (r'x=1', r''),
    (r'2x+3=7 2/3', r''),
    (r'x + x - x = 1 - 2 - 3', r''),
    (r'$\frac{4}{9}$ * X + 0,8 * X + X = 101', r''),
    (r'x + 0.123456789 = 0.123456709', r''),
    (r'(2+3)*x + 3*(x+2) = (x+1)*4 - 3x', r''),
    (r'ay + 2y = a + 3 + y', r''),
    (r'x + 2a = 3', r''),
    (r'(x+1)/(x+1) = 0', r''),
    (r'1/(x+1) + 1/2 + 1/3 = 3', r''),
    (r'1/(x+t) = 3', r''),
    (r'(x+3)/4 + 1/2 = (x-5)/8', r''),
    # (r'Собранный пул - условия', r'Ответы'),
    (r'x = 2', r'x = 2'),
    (r'x - 2 = 0', r'x = 2'),
    (r'2x = 4', r'x = 2'),
    (r'2x - 4 = 0', r'x = 2'),
    (r'(37+x) - 58 = 49', r'x = 70'),
    (r'325-(x-617)=219', r'x = 723'),
    (r'228:x=12', r'x = 19'),
    (r'(x-3):4=6', r'x = 27'),
    (r'36:(x-2)=4', r'x = 11'),
    (r'7(x-5)=63', r'x = 14'),
    (r'16x-x+14=299', r'x = 19'),
    (r'(17/28-x)-11/28=3/28', r'x = 3/28'),
    (r'36/x=4', r'x = 9'),
    (r'4 5/14 - (x - 7 3/14) = 2 9/14', r'x = 8 13/14'),
    (r'(1,24-x)*3,6=3,888', r'x = 0,16'),
    (r'1,1:(x+0,14)=2,5', r'x = 0,3'),
    (r'10 5/8 - x = 7 3/5', r'x = 3 1/40'),
    (r'(x - 2 7/8) + 3 5/6 = 4 2/3', r'x = 3 17/24'),
    (r'5 1/4 : x = 7/8', r'x = 6'),
    (r'3/8 x+15=1/6 x+10', r'x = -24'),
    (r'0,8x+14=2-1,6x', r'x = -5'),
    (r'(13x-15)-(9+6x)=-3x', r'x = 2,4'),
    (r'2/3(1/3 x-1/2)=4x+2 1/2', r'x = -3/4'),
    (r'(0,5x+1,2)-(3,6-4,5x)=(4,8-0,3x)+(10,5x+0,6)', r'x = -1,5'),
    (r'3x-(10+5x)=54', r'x = -32'),
    (r'(5,3x-0,8)-(1,6-4,7x)=2x-(x-0,3)', r'x = 0,3'),
    (r'(x+3)^2 - x(x+4)=24', r'x = 7,5'),
    (r'-13 + 2 4/5 = 2x +1/2 (x+3)', r'x = -4,68'),
    (r'2*(3-8) = 5x + 0,2', r'x = -2,04'),
    (r'1/6 x+1/3 x = -3 + 8,4', r'x = 10,8'),
    (r'2/5 x - 8,5x = 2(-1/3+0,2)', r'x = 8/243'),
    # (r'Случаи исключения', r''),
    (r'x+1=x-1', r'Корней нет'),
    (r'2(x+4)=8+2x', r'$x$ — любое'),
    (r'6x-(x-1)=4+5x', r'Корней нет'),
    (r'5/x=0', r'Корней нет'),
    # (r'параметр', r''),
    (r'x+2a=8', r'x = -2a+8'),
    (r'ax - 4 = 2x', r'$x = \frac{4}{-2 + a}$ при $a ≠ 2$, при $a = 2$ корней нет'),
    (r'ax = 5', r'$x = \frac{5}{a}$ при $a ≠ 0$, при $a = 0$ корней нет'),
    (r'ax = a', r'$x = 1$ при $a ≠ 0$, при $a = 0$ любое число является корнем'),
    (
        r'a(a-3)x = a',
        r'$x = \frac{1}{-3 + a}$ при $a ≠ 0, 3$, при $a = 3$ корней нет, при $a = 0$ любое число является корнем',
    ),
]


class Test(tests_wrapper.TestSolver):
    def setUp(self):
        self.worker = mathsolvers.MathWorker()

    def test_timeout(self):
        res = self.worker.solve('2**10 + x= 4**4', timeout=2)
        print(res)
        self.assertTrue(res and 'error' not in res)
        res = self.worker.solve('2**1000**1000 + x + 1000000! = 4**499**511', timeout=0.1)
        print(res)
        self.assertTrue(res and 'error' in res)
        res = self.worker.solve('2**10 + x = 4**4', timeout=2)
        print(res)
        self.assertTrue(res and 'error' not in res)
        res = self.worker.solve('2**10 + x = 4**4', timeout=2)
        print(res)
        self.assertTrue(res and 'error' not in res)
        res = self.worker.solve('2**1000**1000 + x = 4**499**511 + 1000000!', timeout=0.1)
        print(res)
        self.assertTrue(res and 'error' in res)
        res = self.worker.solve('2**10 + x = 4**4', timeout=2)
        print(res)
        self.assertTrue(res and 'error' not in res)


def add_test_methods():
    for i, (expr, ans) in enumerate(cases):

        def test_solve_with_timeout(self, expr=expr, ans=ans):
            res = mathsolvers.solve(expr)
            resa = self.worker.solve(expr, timeout=2)
            self.assertIsNotNone(res)
            self.assertDictEqual(res, resa)
            if ans:
                final = res.get('final_answer', '').strip(' $')
                are_equal = ans.strip(' $') == final
                if not are_equal:
                    equiv = mathsolvers.check_equivalence(ans, final)
                    are_equal = equiv.get('are_equal', False)
                self.assertTrue(are_equal, f'\n{expr} -> (corr) {ans} ≠ {final} (api)')

        test_solve_with_timeout.__name__ = tests_wrapper.tnesc(f'test_solve_linear_{i + 1:03}: {expr}')

        setattr(Test, test_solve_with_timeout.__name__, test_solve_with_timeout)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
