import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    # expr, (latex, doit, expand, simplify, evalf)
    (
        r'(1+2)+3',
        {
            'latex': r'(1 + 2) + 3',
            'doit': '6',
            'expand': '6',
            'simplify': '6',
            'evalf': 6.0,
        },
    ),
    (
        r'-6 + (1+2)+3',
        {
            'latex': r'-6 + (1 + 2) + 3',
            'doit': '0',
            'expand': '0',
            'simplify': '0',
            'evalf': 0.0,
        },
    ),
    (
        r'x + (y - x) + y',
        {
            'latex': r'x + (y - x) + y',
            'doit': '2 y',
            'expand': '2 y',
            'simplify': '2 y',
            'evalf': None,
        },
    ),
    (
        r'(x - y) (x + y)',
        {
            'latex': r'(x - y) (x + y)',
            'doit': r'(x + y) (x - y)',
            'expand': 'x^{2} - y^{2}',
            'simplify': 'x^{2} - y^{2}',
            'evalf': None,
        },
    ),
    (
        r'(sin x) - sin( (x) )',
        {
            'latex': r'(\sin{(x )}) - \sin{((x) )}',
            'doit': r'0',
            'expand': '0',
            'simplify': '0',
            'evalf': None,
        },
    ),
    (
        r'-(-2)**2 - (-3)**(2)',
        {
            'latex': r'- (-2)^{2} - (-3)^{2}',
            'doit': r'-13',
            'expand': '-13',
            'simplify': '-13',
            'evalf': None,
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

        def test_parenthesis(self, expr=expr, ans=ans):
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

        test_parenthesis.__name__ = tests_wrapper.tnesc(f'test_parenthesis_{i + 1:03}: {expr}')
        setattr(Test, test_parenthesis.__name__, test_parenthesis)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
