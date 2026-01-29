import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper
from mathsolvers.sympy_stuff.utils import srepr

cases = [
    # Базовые случаи
    (r"2/a*b", r"(2/a)*b"),
    (r"1 + 2/a*b + 2", r"1 + (2/a)*b + 2"),
    (r"2/ab", r"2/(a*b)"),
    (r"1 + 2/ab + 2", r"1 + 2/(a*b) + 2"),
    (r"ab/ab", r"(a*b)/(a*b)"),
    (r"1 + ab/ab + 2", r"1 + (a*b)/(a*b) + 2"),
    (r"abc/abc", r"(a*b*c)/(a*b*c)"),
    (r"1 + abc/abc + 2", r"1 + (a*b*c)/(a*b*c) + 2"),

    # Многосимвольные выражения
    (r"a/bc", r"a/(b*c)"),
    (r"abcd/efgh", r"(a*b*c*d)/(e*f*g*h)"),

    (r"(ab)^2/cd", r"(a*b)**2/(c*d)"),

    # Комбинированные операции
    (r"2/ab * cd/ef", r"(2/(a*b))*(c*d/(e*f))"),
    (r"ab/cd + ef/gh", r"(a*b)/(c*d) + (e*f)/(g*h)"),
    (r"a/b c/d + e/f g/h", r"(a/b)*(c/d) + (e/f)*(g/h)"),

    # Числовые коэффициенты
    (r"2ab/3cd", r"(2*a*b)/(3*c*d)"),
    (r"5xy/6zt", r"(5*x*y)/(6*z*t)"),

    # Вложенные дроби
    (r"a/(b/cd)", r"a/(b/(c*d))"),
    (r"(a/bc)/(d/ef)", r"(a/(b*c))/(d/(e*f))"),
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (expr1, expr2) in enumerate(cases):
        def test_implicit_mul(self, expr1=expr1, expr2=expr2):
            res = mathsolvers.check_equivalence(expr1, expr2)
            p1 = mathsolvers.parse(expr1)
            p2 = mathsolvers.parse(expr2)
            print(srepr(p1), mathsolvers.hum(p1))
            print(srepr(p2), mathsolvers.hum(p2))
            self.assertTrue(res['are_equal'])

        test_implicit_mul.__name__ = tests_wrapper.tnesc(f'test_implicit_mul_{i + 1:03}: {expr1} {expr2}')
        setattr(Test, test_implicit_mul.__name__, test_implicit_mul)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
