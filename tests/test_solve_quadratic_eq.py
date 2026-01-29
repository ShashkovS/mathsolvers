import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    (r'x^2 = 4', r'$x = -2; x = 2$'),
    (r'x^2 - 4 = 0', r'$x = -2; x = 2$'),
    (r'-4 = -x^2', r'$x = -2; x = 2$'),
    (r'0 = x^2 - 4', r'$x = -2; x = 2$'),
    (r'x^2 - 2 = 2', r'$x = -2; x = 2$'),
    (r'2x^2 = 4 + x^2', r'$x = -2; x = 2$'),
    (r'x^2 + 187x = 4 + 187x', r'$x = -2; x = 2$'),
    (r'2x^2 = 8', r'$x = -2; x = 2$'),
    (r'-x^2 = -4', r'$x = -2; x = 2$'),
    (r'x^2 + x = x', r'$x = 0$'),
    (r'x^2 = 8', r'$x = -2 \sqrt{2}; x = 2 \sqrt{2}$'),
    (r'x^2 - x = 0', r'$x = 0; x = 1$'),
    (r'-x^2 - x = 0', r'$x = -1; x = 0$'),
    (r'2x^2 - 3x = 0', r'$x = 0; x = \frac{3}{2}$'),
    (r'2x^2 = 3x', r'$x = 0; x = \frac{3}{2}$'),
    (r'x^2 - 2x + 3 = 3 - x', r'$x = 0; x = 1$'),
    (r'x = 2x^2', r'$x = 0; x = \frac{1}{2}$'),
    (r'x-3 = 4x^2 - 3', r'$x = 0; x = \frac{1}{4}$'),
    (r'1/(x+1) + 1/(x-2) = 3', r'$x = \frac{1}{6} (5-\sqrt{85}); x = \frac{1}{6} (5+\sqrt{85})$'),
    (r'x^2 + 2x + 1 = 0', r'$x = -1$'),
    (r'(x+1)(x+2)=0', r'$x = -2; x = -1$'),
    (r'x^2 + 3x = -2', r'$x = -2; x = -1$'),
    (r'3x^2-7x+4=0', r'$x = 1; x = \frac{4}{3}$'),
    (r'5x^2-8x+3=0', r'$x = \frac{3}{5}; x = 1$'),
    (r'3x^2-13x+14=0', r'$x = 2; x = \frac{7}{3}$'),
    (r'2y^2-9y+10=0', r'$y = 2; y = \frac{5}{2}$'),
    (r'5y^2-6y+1=0', r'$y = \frac{1}{5}; y = 1$'),
    (r'4x^2+x-33=0', r'$x = -3; x = \frac{11}{4}$'),
    (r'y^2-10y-24=0', r'$y = -2; y = 12$'),
    (r'p^2+p-90=0', r'$p = -10; p = 9$'),
    (r'14x^2-5x-1=0', r'$x = -\frac{1}{7}; x = \frac{1}{2}$'),
    (r'-y^2+3y+5=0', r'$y = \frac{1}{2} (3-\sqrt{29}); y = \frac{1}{2} (3+\sqrt{29})$'),
    (r'2x^2+x+67=0', r'$x = \frac{1}{4} (-1-i \sqrt{535}); x = \frac{1}{4} (-1+i \sqrt{535})$'),
    (r'1-18p+81p^2=0', r'$p = \frac{1}{9}$'),
    (r'-11y+y^2-152=0', r'$y = -8; y = 19$'),
    (r'18+3x^2-x=0', r'$x = \frac{1}{6} (1-i \sqrt{215}); x = \frac{1}{6} (1+i \sqrt{215})$'),
    (r'5x^2-11x+2=0', r'$x = \frac{1}{5}; x = 2$'),
    (r'2p^2+7p-30=0', r'$p = -6; p = \frac{5}{2}$'),
    (r'9y^2-30y+25=0', r'$y = \frac{5}{3}$'),
    (r'35x^2+2x-1=0', r'$x = -\frac{1}{5}; x = \frac{1}{7}$'),
    (r'2y^2-y-5=0', r'$y = \frac{1}{4} (1-\sqrt{41}); y = \frac{1}{4} (1+\sqrt{41})$'),
    (r'16x^2-8x+1=0', r'$x = \frac{1}{4}$'),
    (r'3x^2-14x+16=0', r'$x = 2; x = \frac{8}{3}$'),
    (r'5p^2-16p+3=0', r'$p = \frac{1}{5}; p = 3$'),
    (r'd^2+2d-80=0', r'$d = -10; d = 8$'),
    (r'x^2-22x-23=0', r'$x = -1; x = 23$'),
    (r'4t^2-36t+77=0', r'$t = \frac{7}{2}; t = \frac{11}{2}$'),
    (r'15y^2-22y-37=0', r'$y = -1; y = \frac{37}{15}$'),
    (r'7z^2-20z+14=0', r'$z = \frac{1}{7} (10-\sqrt{2}); z = \frac{1}{7} (10+\sqrt{2})$'),
    (r'y^2-10y-25=0', r'$y = 5 (1-\sqrt{2}); y = 5 (1+\sqrt{2})$'),
    (r'8x^2-14x+5=0', r'$x = \frac{1}{2}; x = \frac{5}{4}$'),
    (r'12t^2+16t-3=0', r'$t = -\frac{3}{2}; t = \frac{1}{6}$'),
    (r'4p^2+4p+1=0', r'$p = -\frac{1}{2}$'),
    (r'x^2-8x-84=0', r'$x = -6; x = 14$'),
    (r'm^2+6m-19=0', r'$m = -3-2 \sqrt{7}; m = 2 \sqrt{7}-3$'),
    (r'5y^2+26y-24=0', r'$y = -6; y = \frac{4}{5}$'),
    (r'z^2-34z+289=0', r'$z = 17$'),
    (r'3x^2+32x+80=0', r'$x = -\frac{20}{3}; x = -4$'),
    (r'2x^2-5x-3=0', r'$x = -\frac{1}{2}; x = 3$'),
    (r'3x^2-8x+5=0', r'$x = 1; x = \frac{5}{3}$'),
    (r'5x^2+9x+4=0', r'$x = -1; x = -\frac{4}{5}$'),
    (r'36y^2-12y+1=0', r'$y = \frac{1}{6}$'),
    (r'3t^2-3t+1=0', r'$t = \frac{1}{6} (3-i \sqrt{3}); t = \frac{1}{6} (3+i \sqrt{3})$'),
    (r'x^2+9x-22=0', r'$x = -11; x = 2$'),
    (r'y^2-12y+32=0', r'$y = 4; y = 8$'),
    (r'100x^2-160x+63=0', r'$x = \frac{7}{10}; x = \frac{9}{10}$'),
    (r'25=26x-x^2', r'$x = 1; x = 25$'),
    (r'y^2=4y+96', r'$y = -8; y = 12$'),
    (r'3t^2=10-29t', r'$t = -10; t = \frac{1}{3}$'),
    (r'3p^2+3=10p', r'$p = \frac{1}{3}; p = 3$'),
    (r'x^2-20x=20x+100', r'$x = 10 (2-\sqrt{5}); x = 10 (2+\sqrt{5})$'),
    (r'25x^2-13x=10x^2-7', r'$x = \frac{1}{30} (13-i \sqrt{251}); x = \frac{1}{30} (13+i \sqrt{251})$'),
    (r'(2x-3)⋅(5x+1)=2x+$\frac{2}{5}$', r'$x = -\frac{1}{5}; x = \frac{15 \unicode{22c5}+2}{10 \unicode{22c5}}$'),
    (r'(3y-1)⋅(y+3)=y(1+6y)', r'$\unicode{22c5} = \frac{y (6 y+1)}{3 y^2+8 y-3}$'),
    (r'(t-1)⋅(t+1)=2(5t-10$\frac{1}{2}$)', r'$\unicode{22c5} = \frac{10 t-21}{t^2-1}$'),
    (r'-z(z+7)=(z-2)⋅(z+2)', r'$\unicode{22c5} = \frac{-z^2-7 z}{z^2-4}$'),
    (r'(x+4)^2=3x+40', r'$x = -8; x = 3$'),
    (r'(2p-3)^2=11p-19', r'$p = \frac{7}{4}; p = 4$'),
    (r'3⋅(x+4)^2=10x+32', r'$\unicode{22c5} = \frac{2 (5 x+16)}{3 (x+4)^2}$'),
    (r'(x+1)^2=7918-2x', r'$x = -91; x = 87$'),
    (r'(m+2)^2=3131-2m', r'$m = -59; m = 53$'),
    (r'(x+1)^2=(2x-1)^2', r'$x = 0; x = 2$'),
    (r'(n-2)^2+48=(2-3n)^2', r'$n = -2; n = 3$'),
    (r'0,7x^2=1,3x+2', r'$x = -1; x = 2,85714$'),
    (r'7=0,4y+1/5 y^2', r'$y = -7; y = 5$'),
    (r'x^2-1,6x-0,36=0', r'$x = -0,2; x = 1,8$'),
    (r'z^2-2z+2,91=0', r'$z = 1 -1,38203 i; z = 1 +1,38203 i$'),
    (r'0,2y^2-10y+125=0', r'$y = 25$'),
    (r'$\frac{1}{3}$x^2+2x-9=0', r'$x = -9; x = 3$'),
    (r'(x+1)(x+2)=0', r'$x = -2; x = -1$'),
    (r'2(x+1)(x+2)=0', r'$x = -2; x = -1$'),
    (r'-2(x+1)(x+2)=0', r'$x = -2; x = -1$'),
    (r'(2x+1)(3x+2)=0', r'$x = -\frac{2}{3}; x = -\frac{1}{2}$'),
    (r'2/9(2x+1/3)(3x-2/7)=0', r'$x = -\frac{1}{6}; x = \frac{2}{21}$'),
    (r'$\frac{x^2-4}{4x}$=$\frac{3x-2}{2x}$', r'$x = 6$'),
    # (r'', r''),
    # (r'Собранный пул - условия', r'Ответы'),
    (r'x^2=0', r'$x = 0$'),
    (r'x^2=4/9', r'$x = -\frac{2}{3}; x=\frac{2}{3}$'),
    (r'12=3x^2', r'$x = -2; x=2$'),
    (r'x^2 = -6', r'Корней нет'),
    (r'12x^2 - 5x = 0', r'$x = 0; x=\frac{5}{12}$'),
    (r'x^2-5x-6=0', r'$x = -1; x=6$'),
    (r'2x^2 - x - 1 = 0', r'$x = -0,5; x=1$'),
    (r'4x^2+12x+9=0', r'$x = -1,5$'),
    (r'x^2+4x=-3', r'$x = -3; x=-1$'),
    (r'-x^2+7x+8=0', r'$x = -1; x=8$'),
    (r'(x-1)(x+2)=0', r'$x = 1; x=-2$'),
    (r'4(x-1/2)(x+7/2)=0', r'$x = \frac{1}{2}; x=-\frac{7}{2}$'),
    (r'(x-3)^2 - 4 = 0', r'$x = 1; x=5$'),
    (r'(x+6)^2 - 4(x-5)^2 = 0', r'$x = \frac{4}{3}; x=16$'),
    (r'x^2+x+2 = 0', r'Корней нет'),
    (r'3x^2=27x', r'$x = 0; x=9$'),
    (r'(x-3)(x+1)-5=2x^2-6x-4', r'$x = 2$'),
    (r'(2x^2-3x)/4 = (x^2+2x)/3', r'$x = 0; x=\frac{17}{2}$'),
    (r'0,25x^2-x+1=0', r'$x = 2$'),
    (r'4/49 x^2 + 1 5/7 x + 9 = 0', r'$x = \frac{21}{2}$'),
    (r'2x^2-3x-3=0', r'$x = (3+\sqrt{33})/4; x=(3-\sqrt{33})/4$'),
    (r'x^2-3x-5-sqrt(7)=0', r'$x = 2+\sqrt{7}; x=1-\sqrt{7}$'),
    (r'x^2-3sqrt(2)x+4=0', r'$\sqrt{2}; x=\2sqrt{2}$'),
    (r'(3x-2)(x-3)=20', r'$x = -1; x=\frac{14}{3}$'),
    (r'(8x-3)(3x+2)-(2x-3)(8x-2)=33x+20', r'$x = (-1-\sqrt{257})/8; x=(-1+\sqrt{257})/8$'),
    (r'(x-1)^2 / 5-(x+4)/6 = (2x-2)/3', r'$x = \frac{1}{6}; x=6$'),
    (r'5x^2-10x-400=0', r'$x = -8; x=10$'),
    (r'x^2-5000x+4999=0', r'$x = 1; x=4999$'),
    (r'0,2x^2+3,3x-0,668=0', r'$x = -16,7; x=0,2$'),
    (r'(x^2-3)/2-6x=5', r'$x = -1; x=13$'),
    (r'(3x+1)^2-x(7x+5)=4', r'$x = -1; x=\frac{3}{2}$'),
    # (r'Задачи с параметром', r''),
    (r'x^2+ax-2=0', r'x1=(-a-sqrt(a^2+8))/2, x2=(-a+sqrt(a^2+8))/2'),
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (expr, ans) in enumerate(cases):

        def test_solve_with_timeout(self, expr=expr, ans=ans):
            res = mathsolvers.solve(expr)
            resa = self.worker.solve(expr, timeout=2)
            self.assertIsNotNone(res)
            self.assertDictEqual(res, resa)
            # TODO
            if ans:
                final = res.get('final_answer', '')
                are_equal = ans == final
                if not are_equal:
                    final_ans = [mathsolvers.parse(s) for s in final.split(';')]
                    ans_ans = [mathsolvers.parse(s) for s in final.split(';')]
                    if len(final_ans) == len(ans_ans):
                        are_equal = all(
                            mathsolvers.check_equivalence(ff, aa) for (ff, aa) in zip(final_ans, ans_ans, strict=False)
                        )
                        if not are_equal:
                            are_equal = all(
                                mathsolvers.check_equivalence(ff, aa)
                                for (ff, aa) in zip(final_ans, ans_ans.reverse(), strict=False)
                            )
                self.assertTrue(are_equal, f'\n{expr} -> (corr) {ans} ≠ {final} (api)')

        test_solve_with_timeout.__name__ = tests_wrapper.tnesc(f'test_solve_linear_{i + 1:03}: {expr}')

        setattr(Test, test_solve_with_timeout.__name__, test_solve_with_timeout)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
