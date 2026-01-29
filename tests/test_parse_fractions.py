import unittest

from mathsolvers.sympy_stuff import tests_wrapper
from mathsolvers.sympy_stuff import parse_fractions

cases = [
    # не вложенные дроби
    (r'3 + \frac12 + 4', '                    ', r'3 + (1/2) + 4'),
    (r'3 + \frac  1   2 + 4', '               ', r'3 + (1/2) + 4'),
    (r'3 + \frac{1}2 + 4', '                  ', r'3 + (1/2) + 4'),
    (r'3 + \frac { 1 }  2 + 4', '             ', r'3 + (1/2) + 4'),
    (r'3 + \frac1{2} + 4', '                  ', r'3 + (1/2) + 4'),
    (r'3 + \frac 1 { 2 } + 4', '              ', r'3 + (1/2) + 4'),
    (r'3 + \frac {1} {2} + 4', '              ', r'3 + (1/2) + 4'),
    (r'3 + \dfrac12 + 4', '                   ', r'3 + (1/2) + 4'),
    (r'3 + \dfrac{1}2 + 4', '                 ', r'3 + (1/2) + 4'),
    (r'3 + \dfrac1{2} + 4', '                 ', r'3 + (1/2) + 4'),
    (r'3 + \dfrac {1} {2} + 4', '             ', r'3 + (1/2) + 4'),
    (r'3 + \frac\pi2 + 4', '                  ', r'3 + ((\pi)/2) + 4'),
    (r'3 + \frac{\pi}2 + 4', '                ', r'3 + ((\pi)/2) + 4'),
    (r'3 + \frac\pi{2} + 4', '                ', r'3 + ((\pi)/2) + 4'),
    (r'3 + \frac {\pi} {2} + 4', '            ', r'3 + ((\pi)/2) + 4'),
    (r'3 + \frac1\pi + 4', '                  ', r'3 + (1/(\pi)) + 4'),
    (r'3 + \frac{1}\pi + 4', '                ', r'3 + (1/(\pi)) + 4'),
    (r'3 + \frac1{\pi} + 4', '                ', r'3 + (1/(\pi)) + 4'),
    (r'3 + \frac {1} {\pi} + 4', '            ', r'3 + (1/(\pi)) + 4'),
    (r'3 + \frac\pi\phi + 4', '               ', r'3 + ((\pi)/(\phi)) + 4'),
    (r'3 + \frac \pi  \phi + 4', '            ', r'3 + ((\pi)/(\phi)) + 4'),
    (r'3 + \frac{\pi}\phi + 4', '             ', r'3 + ((\pi)/(\phi)) + 4'),
    (r'3 + \frac\pi{\phi} + 4', '             ', r'3 + ((\pi)/(\phi)) + 4'),
    (r'3 + \frac {\pi} {\phi} + 4', '         ', r'3 + ((\pi)/(\phi)) + 4'),
    (r'3 + \frac1{\sqrt{2}} + 4', '           ', r'3 + (1/(\sqrt{2})) + 4'),
    (r'3 + \frac{\sqrt{1}}2 + 4', '           ', r'3 + ((\sqrt{1})/2) + 4'),
    (r'3 + \cfrac{-1}2 + 4', '                ', r'3 + ((-1)/2) + 4'),
    (r'3 + \dfrac { -1 }  2 + 4', '           ', r'3 + ((-1)/2) + 4'),
    (r'3 + \frac1{-2} + 4', '                 ', r'3 + (1/(-2)) + 4'),
    (r'3 + \frac 1 { -2 } + 4', '             ', r'3 + (1/(-2)) + 4'),
    (r'3 + \frac {-1} {-2} + 4', '            ', r'3 + ((-1)/(-2)) + 4'),
    (r'3 + \frac x2 + 4', '                   ', r'3 + (x/2) + 4'),
    (r'3 + \frac{x}2 + 4', '                  ', r'3 + (x/2) + 4'),
    (r'3 + \frac x{2} + 4', '                 ', r'3 + (x/2) + 4'),
    (r'3 + \dfrac x 2 + 4', '                 ', r'3 + (x/2) + 4'),
    (r'3 + \frac1y + 4', '                    ', r'3 + (1/y) + 4'),
    (r'3 + \frac{1}y + 4', '                  ', r'3 + (1/y) + 4'),
    (r'3 + \frac1{y} + 4', '                  ', r'3 + (1/y) + 4'),
    (r'3 + \dfrac{x}{y} + 4', '               ', r'3 + (x/y) + 4'),
    (r'3 + \frac x y + 4', '                  ', r'3 + (x/y) + 4'),
    (r'3 + \frac{x}y + 4', '                  ', r'3 + (x/y) + 4'),
    (r'3 + \frac x{y} + 4', '                 ', r'3 + (x/y) + 4'),
    (r'3 + \dfrac x y + 4', '                 ', r'3 + (x/y) + 4'),
    (r'\frac{a - b}{ac}', '                   ', r'((a - b)/(ac))'),
    (r'\frac{a - b}{2c}', '                   ', r'((a - b)/(2c))'),
    (r'\frac{a - b}{a+c}', '                   ', r'((a - b)/(a+c))'),
    # вложенные дроби
    (r'3 + \frac{\frac12}2 + 4', '            ', r'3 + ((1/2)/2) + 4'),
    (r'3 + \frac1{\frac12} + 4', '            ', r'3 + (1/(1/2)) + 4'),
    (r'3 + \frac{\frac12}{\frac12} + 4', '    ', r'3 + ((1/2)/(1/2)) + 4'),
    # несколько дробей
    (r'1 + \frac{1}{4}*x - \frac{1}{2}', '    ', r'1 + (1/4)*x - (1/2)'),
    (
        r'1 + \frac{\frac{3}{4} + \frac{5}{6}}{2}*x - \frac{3}{4} + \frac{5}{\frac{3}{4} + \frac{5}{6}}',
        '',
        r'1 + (((3/4) + (5/6))/2)*x - (3/4) + (5/((3/4) + (5/6)))',
    ),
    # смешанные дроби
    (r'3 + 8 \frac12 + 4', '                    ', r'3 + (8 1/2) + 4'),
    (r'3 + 8\frac  1   2 + 4', '                ', r'3 + (8 1/2) + 4'),
    (r'3 + 8 \frac{1}2 + 4', '                  ', r'3 + (8 1/2) + 4'),
    (r'3 + 8 \frac { 1 }  2 + 4', '             ', r'3 + (8 1/2) + 4'),
    (r'3 + 8 \frac1{2} + 4', '                  ', r'3 + (8 1/2) + 4'),
    (r'3 + 8 \frac 1 { 2 } + 4', '              ', r'3 + (8 1/2) + 4'),
    (r'3 + 8 \frac {1} {2} + 4', '              ', r'3 + (8 1/2) + 4'),
    (r'3 + 8\dfrac12 + 4', '                    ', r'3 + (8 1/2) + 4'),
    (r'3 + 8 \dfrac{1}2 + 4', '                 ', r'3 + (8 1/2) + 4'),
    (r'3 + 8 \dfrac1{2} + 4', '                 ', r'3 + (8 1/2) + 4'),
    (r'3 + 8 \dfrac {1} {2} + 4', '             ', r'3 + (8 1/2) + 4'),
    (r'3 + 8 \frac x2 + 4', '                   ', r'3 + (8 x/2) + 4'),
    (r'3 + 8 \frac{x}2 + 4', '                  ', r'3 + (8 x/2) + 4'),
    (r'3 + 8 \frac x{2} + 4', '                 ', r'3 + (8 x/2) + 4'),
    (r'3 + 8 \dfrac x 2 + 4', '                 ', r'3 + (8 x/2) + 4'),
    (r'3 + 8 \frac1y + 4', '                    ', r'3 + (8 1/y) + 4'),
    (r'3 + 8 \frac{1}y + 4', '                  ', r'3 + (8 1/y) + 4'),
    (r'3 + 8 \frac1{y} + 4', '                  ', r'3 + (8 1/y) + 4'),
    (r'3 + 8 \dfrac{x}{y} + 4', '               ', r'3 + (8 x/y) + 4'),
    (r'3 + 8 \frac x y + 4', '                  ', r'3 + (8 x/y) + 4'),
    (r'3 + 8 \frac{x}y + 4', '                  ', r'3 + (8 x/y) + 4'),
    (r'3 + 8 \frac x{y} + 4', '                 ', r'3 + (8 x/y) + 4'),
    (r'3 + 8 \dfrac x y + 4', '                 ', r'3 + (8 x/y) + 4'),
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (expr, _, ans) in enumerate(cases):

        def test_parse_fraction(self, expr=expr, ans=ans):
            res = parse_fractions.convert_fractions(expr)
            self.assertEqual(res, ans)

        test_parse_fraction.__name__ = tests_wrapper.tnesc(f'test_parse_fraction_{i + 1:03}: {expr}')
        setattr(Test, test_parse_fraction.__name__, test_parse_fraction)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
