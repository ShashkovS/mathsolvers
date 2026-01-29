# flake8: noqa: E501
import unittest

import sympy

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper
from mathsolvers.sympy_stuff import utils

cases = [
    # 1 отовсюду убираются
    (r'1', r'', r''),
    (r'x', r'x', r''),
    (r'1*2', r'2', r''),
    (r'2*x*3*y', r'2; x; 3; y', r''),
    (r'1/2', r'', r'2'),
    (r'x/y', r'x', r'y'),
    (r'2/3 * 4/5', r'2; 4', r'3; 5'),
    (r'2/3 * x/y', r'2; x', r'3; y'),
    (r'2^5', r'2^{5}', r''),
    (r'2^(-5)', r'', r'2^{5}'),
    (r'1/2^5', r'', r'2^{5}'),
    (r'1/2^(-5)', r'2^{5}', r''),
    ('1', '', ''),
    ('2', '2', ''),
    ('1/2', '', '2'),
    ('2/3', '2', '3'),
    ('a/b', 'a', 'b'),
    ('a^{2}/(b^{2})', 'a^{2}', 'b^{2}'),
    ('a^{2}/b^{2}', 'a^{2}', 'b^{2}'),
    ('24*c^{2}*d^{2}/((36*a*c))', '24; c^{2}; d^{2}', '36; a; c'),
    ('(a/b)^3', 'a^{3}', 'b^{3}'),
    ('a^2 b^(-2)', 'a^{2}', 'b^{2}'),
    ('(2.5 * 3/5)/(3.5 * 7/9)', '2.5; 3; 9', '5; 3.5; 7'),
    ('(2/3)/(5/7) * ((11/13)/(15/17))/(19/23)', '2; 7; 11; 17; 23', '3; 5; 13; 15; 19'),
    ('x^n⋅x^3', '', ''),
    ('a^2 / a^8', '', ''),
    ('(3*x)/(2*y^2) * (4*z)/(5*w)', '3; x; 4; z', '2; y^{2}; 5; w'),
    ('((7^3)/(2^2)) * (5/(3^2))', '7^{3}; 5', '2^{2}; 3^{2}'),
    ('(x^3/y^(-2)) * (z/(a^2))', 'x^{3}; y^{2}; z', 'a^{2}'),
    ('(2^(-3)/3^2) * (4/(x*y))', '4', '2^{3}; 3^{2}; x; y'),
    ('(1/(2^3)) * (3/(4^(-2)))', '3; 4^{2}', '2^{3}'),
    ('((5*x)/(3*y))^2', '5^{2}; x^{2}', '3^{2}; y^{2}'),
    ('(a^(-1)/b^3) * (c/(d^(-2)))', 'c; d^{2}', 'a; b^{3}'),
    ('(2^3/(3*4^2)) * (x/(y^2*z))', '2^{3}; x', '3; 4^{2}; y^{2}; z'),
    ('(3/4)/(5^2/(7*x)) * (9^(-1)/y^3)', '3; 7; x', '4; 5^{2}; 9; y^{3}'),
    ('(a*b)/(c*d) * ((e/f)/(g/h))', 'a; b; e; h', 'c; d; f; g'),
    ('(2^(-2)/3) * (4/(5^(-1)))', '4; 5', '2^{2}; 3'),
    ('(x^(3/2)/y^(1/2)) * (z/(w^(5/3)))', 'x^{\\frac{3}{2}}; z', '\\sqrt{y}; w^{\\frac{5}{3}}'),
    ('(5/(6*x^2)) * (7^2/(2*y^3))', '5; 7^{2}', '6; x^{2}; 2; y^{3}'),
    ('(1/(3^(-2))) * (2^(-3)/(4*x))', '3^{2}', '2^{3}; 4; x'),
    ('(a^(-1)/b^2) * (c/(d^(-3)))', 'c; d^{3}', 'a; b^{2}'),
    ('(2/(3^2)) * (4^(-1)/(x*y^2))', '2', '3^{2}; 4; x; y^{2}'),
    ('(x/(y^(-3))) * (z^2/(w^(-2)))', 'x; y^{3}; z^{2}; w^{2}', ''),
    ('(a^2*b^(-3))/(c^(-2)*d^3)', 'a^{2}; c^{2}', 'b^{3}; d^{3}'),
    ('(2^3/(3^(-2)*4)) * (x/(y^2*z^3))', '2^{3}; 3^{2}; x', '4; y^{2}; z^{3}'),
    ('(a^(5/2)/(b^(3/2))) * (c/(d^(1/2)))', 'a^{\\frac{5}{2}}; c', 'b^{\\frac{3}{2}}; \\sqrt{d}'),
    # Теперь жесть без ответа
    ('((2^(-3)/((x^(2/3))*y^(-1/2)))/(z^(4/5)/5^(-2))) * ((7^3 * a^(-5))/(b^(3/2) * c^(-7)))', None, None),
    ('(((3*x^(-2))/(4*y^3))^(-3) * ((z^2)/(w^(5/3)))^3) / (((a^2)/(b^(-3/2))) * ((c*d^(-2))/(e*f^(-1))))', None, None),
    (
        '(((3*x^(-2))/(4*y^3))^(-1/2) * ((z^2)/(w^(5/3)))^3) / (((a^2)/(b^(-3/2))) * ((c*d^(-2))/(e*f^(-1))))',
        None,
        None,
    ),
    ('(((2^(-5)*x^(4/3))/(y^(2/5)*z^(3/4)))/(w^(-7/3)*v^(1/4)))^(-2) * (((a^(-3)/b^2)/(c^(-5/2)/d^3))^3)', None, None),
    ('((x^(-1/2) * y^(3/4))/(z^(-2/3) * w^(5/6)))^(-3) * (((a^2)/(b^(-3/5)))^(-1/2) * (c/(d^2))^(-2))', None, None),
    ('((3^(-4) * x^2)/(5^(-3) * y^(7/2)))^(-2/3) / (((z^(-5) * w^2)/(v^(-3) * u^(-4)))^3)', None, None),
    (
        '(((2^(-7) * x^(-3/2))/(3^(2/3) * y^5))^(-3/4) * ((z^(4/3))/(w^(-7/2)))^(-1/2)) / (((a^(-5) * b^(-3/4))/(c^(2/3) * d^(-1/2)))^(-5))',
        None,
        None,
    ),
    (
        '(((2^(-5/2) * x^3)/(y^(-7/4) * z^(2/3)))/(w^(-5/2) * v^(-3/4)))^(-4) / (((a^5 * b^(-7/3))/(c^(-1/3) * d^(-5/6)))^(-2))',
        None,
        None,
    ),
    (
        '(((3^(-5/4) * x^(-7/5))/(y^(4/3) * z^(5/7)))/(w^(-2/3) * v^3))^(-5/6) * (((a^(-3/2) * b^(7/4))/(c^(5/3) * d^(-7/2)))^(-4/3))',
        None,
        None,
    ),
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (expr, ans_numer, ans_denom) in enumerate(cases):

        def test_split_numer_denom(self, expr=expr, ans_numer=ans_numer, ans_denom=ans_denom):
            parsed = mathsolvers.parse(expr)
            numer, denom = utils.split_numer_denom(parsed)
            numer_s = '; '.join(utils.lat(el, comma='.') for el in numer)
            denom_s = '; '.join(utils.lat(el, comma='.') for el in denom)
            if ans_numer:
                self.assertTupleEqual((ans_numer, ans_denom), (numer_s, denom_s))
            print()
            print('e', expr)
            print('n', numer_s)
            print('d', denom_s)
            new_expr = sympy.Mul(*numer, *(sympy.Pow(arg, -1, evaluate=False) for arg in denom), evaluate=False)
            are_equal = mathsolvers.check_equivalence(utils.lat(new_expr), expr)['are_equal']
            print(are_equal)
            self.assertTrue(are_equal)

        test_split_numer_denom.__name__ = tests_wrapper.tnesc(f'test_split_numer_denom_{i + 1:03}: {expr}')

        setattr(Test, test_split_numer_denom.__name__, test_split_numer_denom)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
