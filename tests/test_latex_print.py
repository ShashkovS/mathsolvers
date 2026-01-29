import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    (r'1 + 2', r'1 + 2'),
    (r'1/2', r'\frac{1}{2}'),
    (r'-1/2', r'-\frac{1}{2}'),
    (r'1 1/2', r'1\frac{1}{2}'),
    (r'-1 1/2', r'-1\frac{1}{2}'),
    (r'(1/2) * (3/4)', r'(\frac{1}{2}) (\frac{3}{4})'),
    (r'(2x/3)', r'(\frac{2 x}{3})'),
    (r'(2x/(3y))', r'(\frac{2 x}{3 y})'),
    (r'\frac{2^3}{3^5}', r'\dfrac{2^{3}}{3^{5}}'),
    (r'\frac{2/3}{4/5}', r'\dfrac{\, \frac{2}{3}\, }{\frac{4}{5}}'),
    (r'\frac{2/3 + 1}{4/5 + 2}', r'\dfrac{\, \frac{2}{3} + 1\, }{\frac{4}{5} + 2}'),
    (r'm(x+y)', r'm (x + y)'),
    (r'1/\sqrt[3]{v}', r'\frac{1}{\sqrt[3]{v}}'),
    (r'2!3', r'2! \cdot 3'),
    (r'-2x', '-2 x'),
    (r'1 : 1 2/3', r'1 \div (1\frac{2}{3})'),
    # (r'a^{-2}: a^{6}', ''),  #TODO :(
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (expr, ans) in enumerate(cases):

        def test_latex_print(self, expr=expr, ans=ans):
            parsed = mathsolvers.parse(expr)
            tex = mathsolvers.lat(parsed)
            # txt = mathsolvers.hum(parsed)
            # print(f'\n{expr} = ${tex}$ =?= $ {ans} $ = {txt}')
            self.assertEqual(ans, tex)

        test_latex_print.__name__ = tests_wrapper.tnesc(f'test_latex_print_{i + 1:03}: {expr}')

        setattr(Test, test_latex_print.__name__, test_latex_print)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
