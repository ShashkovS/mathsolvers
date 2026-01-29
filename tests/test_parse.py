import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

# парсим дичь
cases = [
    (r'\frac12', r'\frac{1}{2}'),
    (r'\\frac{1}2', r'\frac{1}{2}'),
    (r'/frac1{2}', r'\frac{1}{2}'),
    (r'3frac{1}{2}', r'3\frac{1}{2}'),
    (r'\cfrac12', r'\frac{1}{2}'),
    (r'\\tfrac12', r'\frac{1}{2}'),
    (r'/tfrac12', r'\frac{1}{2}'),

    ('$12\\text{ дм}^3 6\\text{ см}^3$', r'12 дм^{3} + 6 см^{3}'),
    (r'$12\\text{ дм}^3 6\\text{ см}^3$', r'12 дм^{3} + 6 см^{3}'),
    # юникодное
    (r'√31+1', r'\sqrt{31} + 1'),
    (r'√a+2', r'\sqrt{a} + 2'),
    (r'x²-4 + 2¹²³⁴⁵⁶⁷⁸⁹⁰', r'x^{2} - 4 + 2^{1234567890}'),
    (r'√(2x)⁸', r'(\sqrt{2 x})^{8}'),
    (r'¼ + ⅗', r'\frac{1}{4} + \frac{3}{5}'),
    (r'Х:3,5=1,2:04', r'Х \div (3,5) = (1,2) \div 4'),
    (r'x  2  −5∣x∣+6=0', r'x 2 - 5 |{x}| + 6 = 0'),
    (r'$2\ \frac{5}{12}x=\frac{1}{4}$  ', r'2\frac{5}{12} x = \frac{1}{4}'),
    # большие и меленькие в одном
    (r'X + a + x', r'x + a + x'),
    (r'abcefghiCGIXY', r'a b c e f g h i c g i X Y'),
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (expr, ans) in enumerate(cases):
        def test_parse(self, expr=expr, ans=ans):
            res = mathsolvers.lat(mathsolvers.parse(expr))
            self.assertEqual(res, ans)

        test_parse.__name__ = tests_wrapper.tnesc(f'test_parse_{i + 1:03}: {expr}')
        setattr(Test, test_parse.__name__, test_parse)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
