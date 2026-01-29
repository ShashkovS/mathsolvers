import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    # expr, (latex, doit, expand, simplify, evalf)
    (
        r'(1+2) : 3',
        {
            'latex': r'(1 + 2) \div 3',
            'doit': '1',
            'expand': '1',
            'simplify': '1',
            'evalf': 1.0,
        },
    ),
    (
        r'- 6 : 2 + (1+2) : 3',
        {
            'latex': r'(-6) \div 2 + (1 + 2) \div 3',
            'doit': '-2',
            'expand': '-2',
            'simplify': '-2',
            'evalf': -2.0,
        },
    ),
    (
        r'x + (y - x) : (y - x) - x',
        {
            'latex': r'x + (y - x) \div (y - x) - x',
            'doit': '1',
            'expand': '1',
            'simplify': '1',
            'evalf': None,
        },
    ),
    (
        r'(x^2 - y^2) : (x + y)',
        {
            'latex': r'(x^{2} - y^{2}) \div (x + y)',
            'doit': r'\dfrac{x^{2} - y^{2}}{x + y}',
            'expand': r'\dfrac{x^{2}}{x + y} - \dfrac{y^{2}}{x + y}',
            'simplify': 'x - y',
            'evalf': None,
        },
    ),
    (
        r'(sin x) : sin( (x) )',
        {
            'latex': r'(\sin{(x )}) \div \sin{((x) )}',
            'doit': r'1',
            'expand': '1',
            'simplify': '1',
            'evalf': None,
        },
    ),
    (
        r'-(-2)**2 : (-3)**(2)',
        {
            'latex': r'(- (-2)^{2}) \div (-3)^{2}',
            'doit': r'-\frac{4}{9}',
            'expand': r'-\frac{4}{9}',
            'simplify': r'-\frac{4}{9}',
            'evalf': 2,
        },
    ),
]


class Test(tests_wrapper.TestSolver):
    def test_coeff(self):
        term = mathsolvers.parse('(2x+3)')
        x = mathsolvers.parse('x')
        term.collect(x)
        self.assertEqual(term.coeff(x, 1), 2)
        self.assertEqual(term.coeff(x, 0), 3)


def add_test_methods():
    for i, (expr, ans) in enumerate(cases):

        def test_pdiv(self, expr=expr, ans=ans):
            parsed = mathsolvers.parse(expr)

            latexed = mathsolvers.lat(parsed)
            doited = mathsolvers.lat(parsed.doit())
            expanded = mathsolvers.lat(parsed.expand())
            simplified = mathsolvers.lat(parsed.simplify())
            evalfed = parsed.evalf()
            self.assertEqual(latexed, ans['latex'])
            self.assertEqual(doited, ans['doit'])
            self.assertEqual(expanded, ans['expand'])
            self.assertEqual(simplified, ans['simplify'])
            if isinstance(ans['evalf'], float):
                eq = evalfed == ans['evalf'] or abs(evalfed - ans['evalf']) < 1e-100
            else:
                eq = True
            self.assertTrue(eq, f'{evalfed} ≠ {ans["evalf"]}')

        test_pdiv.__name__ = tests_wrapper.tnesc(f'test_pdiv_{i + 1:03}: {expr}')
        setattr(Test, test_pdiv.__name__, test_pdiv)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
