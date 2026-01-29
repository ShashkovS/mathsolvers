import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper
from mathsolvers.solvers import simplification

cases = [
    r'$\frac{b-c}{b}$+$\frac{b}{b+c}$',
    r'(x + 2y) * (x - y - x)',
    r'1 + (2 + 3) * (4 + 5) * (1+2^2)',
    r'1 + (2 + x) * (4 + x) + (x+2^2)',
    r'2,6 - 1\frac{2}{7}',
    r'2 - 3',
    r'2 + 3 3/4',
    r'2+\frac{3}{4}',
    r'2 - 3',
    r'x+3',
    r'7 2/3 + 1',
    r'\frac{1}{4} * 2',
    r'3,5 * 6,75',
    r'5,9999999999999 + 1',
    r'1 2 / 3 : 2 1 / 3',
    r'1/3 : 5/6',
    r'1/3 + 1/6',
    r'14⋅(3700⋅13-289800÷46)',
    r'6!+6^2',
    r'xy : xy',
    r'12 ⋅ 3 : 9',
    r'$\frac{19}{21}$ - $\frac{17}{21}$ + $\frac{9}{21}$',
    r'$\frac{4}{9}$ \cdot $\frac{63}{64}$ \cdot $\frac{2}{7}$',
    r'2^{-3} - 3^{-2}',
    r'2 1/5 : 1 2/5',
    r'$2 \frac{3}{4}+3,4$',
    r'102,4 : 10,24',
    r'10 000 + 1',
    r'$\biggl({\frac{1}{2}}\,a^{3}b+{\frac{1}{3}}\,a^{2}b-{\frac{1}{4}}\,a\,b^{3}\biggr)\,:5a b$',
    r'12 ⋅ 3 : 9',
    r'630 : 9 ⋅ 3',
    r'560 : 8 ⋅ 5',
    r'14⋅(3700⋅13-289800÷46)',
    r'21⋅(1900⋅23-107300÷37)',
    r'(216 $\cdot$ 28 - 463 680 : 92) : (86 $\cdot$ 64 - 4 496)',
    r'(36 \cdot 207 - 484 338 : 89) : (93 \cdot 71 - 5 598)',
    r'(-3)\cdot(-7) + (-4):(-2)',
    r'(-5)\cdot(-4) + (-6):(-2)',
    r'$\frac{19}{21}$ - $\frac{17}{21}$ + $\frac{9}{21}$',
    r'$\frac{20}{24}$ - $\frac{19}{24}$ + $\frac{18}{24}$',
    r'$\frac{4}{9}$ \cdot $\frac{63}{64}$ \cdot $\frac{2}{7}$',
    r'$\frac{6}{35}$ \cdot $\frac{21}{54}$ \cdot $\frac{3}{5}$',
    r'5 2/7 - 2 6/7',
    r'50 - (2,3256 : 0,068 + 9,38)',
    r'36 - (1,7158 : 0,092 + 12,45)',
    r'-4,8 : (-16) - 0,9 ⋅ 6 + 4,48 : 0,4',
    r'-3,2 : (-8) - 0,6 ⋅ 9 + 3,36 : 0,6',
    r'5!-5^2',
    r'6!+6^2',
    r'(9^{3} - 6^{3})^{2}',
    r'(8^{3} - 4^{3})^{2}',
    r'2^(0.00000003) - 3^(0.00000002)',
    r'$2 $\frac{3}{4}$+3,4$',
    r'$2 \frac{3}{4}+3,4$',
    r'2 3/4+3,4',
    r'1,25 + 1 2/5',
    r'2^{-3} - 3^{-2}',
    r'2$\frac{1}{5}$ : 1$\frac{2}{5}$ ⋅ 5$\frac{1}{2}$ - 4$\frac{2}{7}$ ⋅ $\frac{7}{15}$ ⋅ (1$\frac{1}{2}$)^3',
    r'2 1/5 : 1 2/5 ⋅ 5 1/2 - 4 2/7 ⋅ 7/15 ⋅ (1 1/2)^3',
    r'2 1/5 : 1 2/5',
    r'(2 1/5) : (1 2/5)',
    r'(2 1/5) : (1 2/5) ⋅ (5 1/2) - (4 2/7) ⋅ (7/15) ⋅ (1 1/2)^3',
    r'(2 1/7) : (1 2/7) - (4 2/3) ⋅ (1 1/2)^3',
]

cases_with_subs = [
    r'<<simplify -60x \\ x = 9>>',
    r'<<simplify 12 * y \\ y = 7>>',
    r'<<simplify -60x \\ x = 0,5>>',
    r'<<simplify x + a + 1 = 1 + 3a >>',
    r'<<simplify x + a + 1 = 1 + 3a \\ a = 2>>',
    r'<<simplify x + 1 - a^2 > 1 - 9a \\ a = 1>>',
    r'<<simplify a*(a+1) + x + 1 <= 1 - sqrt(a) \\ a = 4>>',
    r'<<simplify a=a^{2} \\ a = 1>>',
    r'<<simplify a >= a^{2} \\ a = 0>>',
    r'<<simplify a > a^{3} \\ a = 1>>',
    r'<<simplify a < a^{3} \\ a = 0>>',
    r'<<simplify v = s : t \\ t = 5>>',
    r'<<simplify a^{2}=a^{3} \\ a = 1>>',
    r'<<simplify p = a + b + c \\ a = 22>>',
    r'<<simplify p = a + b + c \\ p = 97>>',
    r'<<simplify s = 50 \cdot  t \\ t = 10>>',
    r'<<simplify n + m  \\ n = 21 \\ m = 32>>',
    r'<<simplify 4(x + 6) = x + 9 \\ x = -3>>',
    r'<<simplify a + c \\ a = 5,6 \\ c = 38 >>',
    r'<<simplify (a + 253) \cdot 7 \\ a=124 >>',
    r'<<simplify \frac{30}{5m + 10} \\ m = 3>>',
    r'<<simplify 236 - x \\ x = -6\frac{3}{7}>>',
    r'<<simplify s = nl \\ n = 60 \\ l = 1800>>',
    r'<<simplify 67 - x + y \\ x = 18 \\ y = 25>>',
    r'<<simplify n - (-m)  \\ n = -3,6 \\ m = 7,8>>',
    r'<<simplify |a \cdot b| \\ a = 0,1 \\ b = -2>>',
    r'<<simplify x \cdot y \\ x = 1,2 \\ y = -2,5>>',
    r'<<simplify P = 2(a + b) \\ P = 40 \\ a = 16,23>>',
    r'<<simplify a = bq + r \\ b = 8 \\ q = 14 \\ r = 6 >>',
    r'<<simplify |a \cdot b| \\ a = -\frac{1}{2} \\ b = 3>>',
    r'<<simplify a = bq + r \\ a = 254 \\ q = 31 \\ r = 6 >>',
]

cases_with_answers = [
    # (r'Числовые', r''),
    (r'3+5', r'8'),
    (r'-6+(-4)', r'-10'),
    (r'-8-1/3', r'-25/3'),
    (r'3:5', r'0,6'),
    (r'-2/7', r'-2/7'),
    (r'1/0,000008', r'125000'),
    (r'-2+3^2', r'7'),
    (r'0,5 + 2 * 3/4', r'2'),
    (r'4^2-5^3', r'-109'),
    (r'-2^4+(-3)^2', r'-7'),
    (r'-3^2-(-2)^2-(-4^2)', r'3'),
    (r'3,2*(1,4-2,28):0,04', r'-70,4'),
    (r'(5 8/11 - 3 2/7) : 1 5/28', r'\frac{752}{363}'),
    (r'8^5 / 2^16', r'0,5'),
    (r'3! + 2^4 * 8^6 / 16^5', r'10'),
    (r'3/7-0,1', r'23/70'),
    (r'((1 1/5 : (17/40 + 0,6 - 0,005))*1,7):(5/6+1 1/3 - 1 23/30)+(4,75+7 1/2):(33 : (4 5/7)) : 0,25', r'12'),
    (r'sqrt(0,36)+sqrt(0,01)', r'0,7'),
    (r'(sqrt(4))^2-1,5', r'2,5'),
    (r'sqrt(3^2)+2', r'5'),
    (r'sqrt((-3)^2)+2', r'5'),
    (r'sqrt(4,9*0,9)', r'2,1'),
    # (r'sqrt(1/11)+sqrt(11/13)+sqrt(13/25)', r'0,2'),  # TODO
    (r'(5sqrt(7)-sqrt(63)+sqrt(14))*sqrt(7)', r'14+7sqrt(2)'),
    (r'(sqrt(2)-sqrt(5))*(2sqrt(2)+sqrt(5))', r'- \sqrt{10} - 1'),
    (r'(1-2sqrt(3))^2', r'13-4sqrt(3)'),
    (r'(sqrt(3)-sqrt(6))^2', r'9-6sqrt(2)'),
    # (r'Буквенные', r''),
    (r'x^n * x^3', r'x^{n + 3}'),
    (r'3(x-2)', r'3x-6'),
    (r'2*x*3', r'6x'),
    (r'2x+3y-6x', r'-4x+3y'),
    (r'(2x^2y)^3', r'8 x^{6} y^{3}'),
    (r'(-2 1/7 xy^2)^2', r'225/49 x^2 y^4'),
    (r'(2x-1/3 a)^2', r'4x^2 - 4/3 ax + 1/9 a^2'),
    (r'(-3y-1/3 b)^2', r'9y^2+2by+1/9 b^2'),
    (r'(-3-x)(-3+x)', r'9-x^2'),
    (r'(3a-6)^3', r'27a^3-162a^2+324a-216'),
    (r'x^2 * x^3', r'x^5'),
    (r'xy^2ax^3a^4', r'x^4*y^2*a^5'),
    (r'x^8 : x^3', r'x^5'),
    (r'(-a^5)^3', r'-a^15'),
    (r'(-x^5)^2', r'x^10'),
    (r'2 1/4 a^5 b*(2/3 ab^3)^3', r'2/3 a^8*b^10'),
    (r'-a^2-(3-2a^2)+(7a^2-8)-(5+8a^2)+16', r'0'),
    (r'0,6a^2b(3ab^2-8ab+11a^2b^3)', r'1,8a^3b^3-4,8a^3b^2+6,6a^4b^4'),
    (r'(3a-b)(2a-7b)', r'6a^2-23ab+7b^2'),
    (r'(y-8)(2y-1)-(3y-12)(5y-2)', r'-13y^2+49y-16'),
    (r'sqrt(4x)+sqrt(64x)-sqrt(81x)', r'sqrt(x)'),
    # (r'Буквенные дроби', r''),
    (r'(-63xy^4)/(81xy^4)', r'\frac{- 7}{9}'),  # TODO минус ок?
    (r'(30a^2c^3)/(48a^3c^2)', r'5c/(8a)'),
    (r'(b+c)/3a - (b-2c)/3a', r'c/a'),
    (r'1/a^2+(a-2)/a', r'(a^2-2a+1)/a^2'),
    (r'(9y+1)/(y^2-4)-(y-8)/(4-y^2)+(1-7y)/(y^2-4)', r'3/(y+2)'),
    (r'(3x-5)/x-(3y-2)/y', r'\frac{2}{y} - \frac{5}{x}'),  # TODO (2x-5y)/xy
    (r'6/y-2y', r'(6-2y^2)/y'),
    (r'(a+1)/(a^2-ab)-(1-b)/(b^2-ab)', r'(a+b)/(ab(a-b))'),
    (r'3/(x^2-2x)*(2x-4)/x', r'6/x^2'),
    (r'(x-5)/(3y+5):((x^2-25)/(6y+10))', r'\frac{2}{5 + x}'),
    # (r'(a^2-x^2)/(b^2-16)*((b+4)/(a-x)+x/(4-b)', r'a/(b-4)'),
    (r'(x^2-x-6)/(x^2-3x-10)', r'(x-3)/(x-5)'),
    (r'(9x-x^3)/(x^4-7x^2-18)', r'\dfrac{- x}{2 + x^{2}}'),
]

# TODO
r"""
        '(x + 3) ^ 2 - x(x + 4)',
        '2,06x - 0,6 x',
        '0,5 + 2 * 3/4',
        'x^2 * x^3',
        'x^n * x^3',
        r'\frac{a ^ {2} + a}{a ^ {2} - 9}',
        'a^2 / a^8',
        '(-2 x)^2',
        r'\frac{24d^2 c^2}{36ac}',
        r'(3-2) * 5',
        r'3**7 * 3**12',
        r'<<simplify 2x/x^2 >>',
        r'<<simplify 2*a*b*45 - 3*b*a >>',
        r'<<simplify 2*a:(b*45) - 3*a/b>>',
        r'<<simplify 2*a:b*45 - 3*a/b>>',
        r'<<simplify 2ba - 3 ba>>',
        r'<<simplify 1/b + 1/(ab)>>',
        r'<<simplify $0,36a^{-5}b^{6}c^{3} \cdot \left(-2\frac{2}{9}\right)a^{4}b^{-4}c^{-5}$>>'
"""

to_spreadsheet = ['task\tstep\taction\tanswer\tsolution\tfinal_answer']


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, expr in enumerate(cases):

        def test_step_by_step(self, expr=expr):
            print(f'{expr=}')
            steps, res = mathsolvers.solvers.simplification.step_by_step_and_res(expr)
            # self.print(res)
            self.assertIsNotNone(res)

        def test_step_by_step_str(self, expr=expr):
            print(f'{expr=}')
            res = mathsolvers.solvers.simplification.step_by_step_str(expr)
            print(res)
            self.assertIsNotNone(res)

        def test_simplify_with_timeout(self, expr=expr):
            self.maxDiff = None
            print(f'{expr=}')
            res = mathsolvers.simplify(expr)
            resa = self.worker.simplify(expr, timeout=3)
            self.assertIsNotNone(res)
            self.assertDictEqual(res, resa)

        test_step_by_step.__name__ = tests_wrapper.tnesc(f'test_step_by_step_{i + 1:03}: {expr}')
        setattr(Test, test_step_by_step.__name__, test_step_by_step)
        test_step_by_step_str.__name__ = tests_wrapper.tnesc(f'test_step_by_step_str_{i + 1:03}: {expr}')
        setattr(Test, test_step_by_step_str.__name__, test_step_by_step_str)
        test_simplify_with_timeout.__name__ = tests_wrapper.tnesc(f'test_simplify_with_timeout_{i + 1:03}: {expr}')
        setattr(Test, test_simplify_with_timeout.__name__, test_simplify_with_timeout)

    for i, expr in enumerate(cases_with_subs):

        def test_simplify_subs_with_timeout(self, expr=expr):
            print(f'{expr=}')
            res = mathsolvers.solver(expr)
            resa = self.worker.solver(expr, timeout=3)
            self.assertIsNotNone(res)
            self.assertDictEqual(res, resa)

        test_simplify_subs_with_timeout.__name__ = tests_wrapper.tnesc(
            f'test_simplify_subs_with_timeout_{i + 1:03}: {expr}'
        )
        setattr(Test, test_simplify_subs_with_timeout.__name__, test_simplify_subs_with_timeout)

    for i, (expr, ans) in enumerate(cases_with_answers):

        def test_simplify_answer(self, expr=expr, ans=ans):
            res = simplification.step_by_step_str_and_res(expr)[1]
            are_equal = ans == res
            if not are_equal:
                are_equal = mathsolvers.check_equivalence(ans, mathsolvers.lat(res))['are_equal']
            self.assertTrue(are_equal, f'{expr} -> {mathsolvers.lat(res)} != {ans}')

        test_simplify_answer.__name__ = tests_wrapper.tnesc(f'test_simplify_answer_{i + 1:03}: {expr}')

        setattr(Test, test_simplify_answer.__name__, test_simplify_answer)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
