import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    r'<<solve УРАВНЕНИЕ>>',
    r'<<solve x + 1 = 2 >>',
    r'<<solve p + 2 = 3 - 2p >>',
    r'<<solve 2 \frac{5}{3} x + 0,75 = 0,1(3) + \frac{7}{3} - |-3| >>',
    r'<<solve x^2 - x(x+1) = 7 >>',
    r'<<solve \frac{1}{x} + 2 = 3 >>',
    r'<<solve 2x - a = a - 3 >>',
    r'<<solve 2x^2 -x - 3 = 0 >>',
    r'<<solve x^2 = 4 >>',
    r'<<solve x^2 + 2x = 0 >>',
    r'<<solve x^2 + 2x + 1 = 0 >>',
    r'<<solve (x+1)(x+2) = 0 >>',
    r'<<solve 2x^2 -x - 3 = a >>',
    r'<<solve |x-3| = 2 >>',
    r'<<solve 2x+3=y \\ y-1 = 4x >>',
    r'<<solve 2x < 7 >>',
    r'<<solve x^2 + 2x + 3 > 1 >>',
    r'<<solve 2 < 2x < 7 >>',
    # r'<<solve 2x+3 > 1 \\ x-1 <= 4x >>',  # Пока совсем не работает
    r'<<calc 2 \cdot (1 \frac{1}{3} + 3 \frac{5}{3})>>',
    r'<<calc 24,5 \cdot (\frac{1}{3} + \frac{4}{3}) + \frac{1}{6}>>',
    r'<<calc \frac{5}{12} + \frac{7}{3}>>',
    r'<<calc 7 // 2>>',
    r'<<calc 7 % 2>>',
    r'<<calc 24,5 \div  5>>',
    r'<<calc 7 // 2>>',
    r'<<calc 7 % 2>>',
    r'<<simplify \frac{5}{12} + \frac{7}{3}>>',
    r'<<simplify \frac{(\frac{5}{12} + \frac{7}{3}) ^ 3}{4^3} + 3! - sqrt(24) + |-5| >>',
    r'<<simplify 2 + x \\ x = 5>>',
    r'<<simplify x + y + z \\ x = 5 \\ y = z + 2 \\ z = \frac{1}{2} >>',
    r'<<simplify \frac{2}{4} >>',
    r'<<simplify (x+1)(x+2) - (x-1)(x+7) + x^3 >>',
    r'<<simplify a^3b^5c^23 (a^2 b^7 c^4) >>',
    r'<<simplify \frac{1}{a^{-7}} >>',
    r'<<simplify sqrt(24 \cdot a^2)>>',
    r'<<simplify \frac{1}{\sqrt{2}}>>',
    r'<<simplify \frac{1}{1-\sqrt{2}}>>',
    r'<<factor 2024>>',
    r'<<units 2м 12см + 3м 90см>>',
    r'<<units 3,9 м + 12 см>>',
    r'<<units (2 ч + 5 мин) \cdot 12>>',
    r'<<units 340см \\ дм >>',
    r'<<units 2340кг \\ т >>',
    r'<<units 2340кг \\ т \\ ц >>',
    r'<<units 2340кг \\ т \\ ц \\ г >>',
    r'<<units (10 мин) \cdot 2 \\ ч >>',
    r'<<format \frac{1}{2} \\ dec>>',
    r'<<format 0,5 \\ frac>>',
    # r'<<format 0,(3) \\ frac>>',  # TODO
    r'<<format \frac{1}{3} \\ dec>>',
    r'<<format \frac{10}{6} \\ mix>>',
    r'<<format 1 \frac{4}{6} \\ frac>>',
    r'<<format 0,5 \\ perc>>',
    r'<<format 50% \\ frac>>',
    r'<<format 50% \\ dec>>',
    r'<<compare 3 \\ 5>>',
    r'<<compare 3 \\ (2+3)>>',
    r'<<compare 2 \\ sqrt(5)>>',
    r'<<compare sqrt(5) \\ sqrt(7)>>',
    r'<<compare \frac{1}{6} \\ \frac{1}{7}>>',
    r'<<compare 2a+1 \\ 2a+2>>',
    r'<<compare \frac{3}{5} \\ \frac{2}{7} \\ \frac{3}{4}>>',
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, expr in enumerate(cases):

        def test_to_text(self, expr=expr):
            print(f'\n{expr=}')
            sol = mathsolvers.solver(expr)
            txt = mathsolvers.to_text(sol)
            print(txt)

        test_to_text.__name__ = tests_wrapper.tnesc(f'test_to_text_{i + 1:03}: {expr}')

        setattr(Test, test_to_text.__name__, test_to_text)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
