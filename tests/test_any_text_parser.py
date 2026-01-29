import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    # (expr, solver_call)
    (r'привет', None),
    (r'корень из 144', None),
    (r'$\left(x+y+z\right)=28$', None),
    (r'$x_1+x_2+\ldots+x_{n-1}=x_n$', None),
    (r'y = x^2 -2x + 4', None),
    (r'y\'=x^2', None),
    (r'$e^{\pi\cdot i}=$', None),
    (r'48+(56-х', None),
    (r'0/0', None),
    (r'$x^{-2}=\frac{1}{x^2}<x^0=1$', None),
    (r'бла-бла 2+2', None),
    (r'汉字 2+2', None),
    (r'$11111_2$', None),
    (r'$x^2+4x+7=0$', r'<<solve x^{2} + 4 x + 7 = 0>>'),
    (r'2 + 2 + 5', r'<<simplify 2 + 2 + 5>>'),
    (r'сколько будет 23 + 4 • 4?', r'<<simplify 23 + 4 \cdot 4>>'),
    (r'2=2=', r'<<simplify 2 = 2>>'),
    (r'y^2 - 3x -28=0', r'<<solve y^{2} - 3 x - 28 = 0>>'),
    (r'$3+\frac{7}{2}$', r'<<simplify 3 + \frac{7}{2}>>'),
    (r'реши уравнение 2^x+38324=y*3', r'<<solve 2^{x} + 38324 = y 3>>'),
    (r'Как упростить выражение: (9^6 * (-4)^5)/(-6)^10', r'<<simplify \dfrac{(9^{6} \cdot (-4)^{5})}{(-6)^{10}}>>'),
    (r'Реши пример: 44 : 4 + (6 + 14) - 5 * 0 - 17 * 1 + 14 : (3 + 4) =',
     r'<<simplify 44 \div 4 + (6 + 14) - 5 \cdot 0 - 17 \cdot 1 + 14 \div (3 + 4)>>'),
    (r'Сложи 2+2', r'<<simplify 2 + 2>>'),
    (r'(51−14÷87)×(4−4)', r'<<simplify (51 - 14 \div 87) \cdot (4 - 4)>>'),
    (r'$\sqrt{x+56}=22\times56$', r'<<solve \sqrt{x + 56} = 22 \cdot 56>>'),
    (r'помоги посчитать 20 + 10', r'<<simplify 20 + 10>>'),
    (r'сколько будет 999999936-1000000000', r'<<simplify 999999936 - 1000000000>>'),
    (r'Решить уравнение: x^3 + x^2 - 8x - 8 = 0', r'<<solve x^{3} + x^{2} - 8 x - 8 = 0>>'),
    (r'Как решить уравнение? x=120', r'<<solve x = 120>>'),
    (r'Решить неравенство |x+2|<|x-3|', r'<<solve |{x + 2}| < |{x - 3}|>>'),
    (r'(56+4)+7=', r'<<simplify (56 + 4) + 7>>'),
    (r'2x+3=0', r'<<solve 2 x + 3 = 0>>'),
    (r'2=5-67', r'<<simplify 2 = 5 - 67>>'),
    (r'преобразуй $\sqrt{\frac{2s}{a}}$', r'<<simplify \sqrt{\frac{2 s}{a}}>>'),
    (r'Сократите дробь: $\frac{14 a^{3}}{21 a}$', r'<<simplify \dfrac{14 a^{3}}{21 a}>>'),
    (r'Реши уравнение 5x = 2', r'<<solve 5 x = 2>>'),
    (r'как решить задачу? x!=120', r'<<solve x \neq 120>>'),
    (r'сколько будет 6 * 6 + 4?', r'<<simplify 6 \cdot 6 + 4>>'),
    (r'Напиши ответ 81:9', r'<<simplify 81 \div 9>>'),
    (r'найди корни 3x^2 + 8x -19=0', r'<<solve 3 x^{2} + 8 x - 19 = 0>>'),
    (r'Найди значение $\sqrt{45}$', r'<<simplify \sqrt{45}>>'),
    (r'x:0=3', r'<<solve x \div 0 = 3>>'),
    (r'Реши 2 + 2', r'<<simplify 2 + 2>>'),
    (r'$\left(7\right)>1$', r'<<simplify (7) > 1>>'),
    (r'a) $936 - 579$', r'<<simplify 936 - 579>>'),
    (r'2x2 + 3x', r'<<simplify 2 x^{2} + 3 x>>'),
    (r'2x22 + 3x', r'<<simplify 2 x 22 + 3 x>>'),
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (expr, solver_call) in enumerate(cases):
        def test_and_test_parse(self, expr=expr, solver_call=solver_call):
            res = mathsolvers.check_and_parse(expr)
            if solver_call is None:
                self.assertTrue(res.error)
            else:
                self.assertEqual(res.solver_call, solver_call)

        test_and_test_parse.__name__ = tests_wrapper.tnesc(f'test_and_test_parse_{i + 1:03}: {expr}')
        setattr(Test, test_and_test_parse.__name__, test_and_test_parse)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
