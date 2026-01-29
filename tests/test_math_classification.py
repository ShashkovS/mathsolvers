import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    # (expr, solver, verdict)
    (r'<<calc 2 * 2,7>>', 'calc', 'calc'),
    (r'<<compare | - 5 | \\ | - 12 |>>', 'compare', 'с модулями'),
    (r'<<compare \frac{10}{12} \\ \frac{11}{12}>>', 'compare', 'две дроби'),
    (r'<<compare 0,712 кг \\ 721,5 г>>', 'compare', 'единицы измерения'),
    (r'<<compare \frac{12}{13} \\ \frac{4}{13} \\ \frac{2}{13} \\ \frac{10}{13} >>', 'compare', 'упорядочить много'),
    (r'<<compare sqrt(41) \\ 2sqrt(10)>>', 'compare', 'два корня'),
    (r'<<compare - 104,2 \\ - 101,5>>', 'compare', 'две суммы'),
    (r'<<compare - 0,4 \\ \frac{3}{7}>>', 'compare', 'что-то полухитрое'),
    (r'<<compare 29001 \\ 29002>>', 'compare', 'два целых'),
    (r'<<compare 12,7 \\ 12,5>>', 'compare', 'два десятичных'),
    (r'<<compare - 1,07 \\ - 1,7 \\ 0 \\ reverse>>', 'compare', 'упорядочить в обратном порядке'),
    (r'<<compare 3^{- 1} + 2^{- 1} \\ 5^{- 1}>>', 'compare', 'две степени'),
    (r'<<factor 20>>', 'factor', 'числа'),
    (r'<<factor (6 x - 9 y)^3>>', 'factor', 'хз'),
    (r'<<format 12\frac{5}{6} \\ frac>>', 'format', 'mix -> frac'),
    (r'<<format 0,(02) \\ frac>>', 'format', 'dec (periodic) -> frac'),
    (r'<<format \frac{17}{250} \\ dec>>', 'format', 'frac -> dec'),
    (r'<<format 1\% \\ frac>>', 'format', 'perc -> frac'),
    (r'<<format 24,6 \\ frac>>', 'format', 'dec -> frac'),
    (r'<<format 4\frac{7}{24} \\ dec>>', 'format', 'mix -> dec (periodic)'),
    (r'<<format 5 \\ frac>>', 'format', 'frac -> frac'),
    (r'<<format \frac{1}{2} \\ perc>>', 'format', 'frac -> perc'),
    (r'<<format 9\frac{83}{100} \\ dec>>', 'format', 'mix -> dec'),
    (r'<<format 140 \% \\ mix>>', 'format', 'perc -> mix'),
    (r'<<format \frac{15}{13} \\ mix>>', 'format', 'frac -> mix'),
    (r'<<format \frac{7}{9} \\ dec>>', 'format', 'frac -> dec (periodic)'),
    (r'<<format 3,6 \\ dec>>', 'format', 'dec -> dec'),
    (r'<<format 25 \% \\ dec>>', 'format', 'perc -> dec'),
    (r'<<format - 1,6 : (- 1,2) \\ dec>>', 'format', 'dec -> dec (periodic)'),
    (r'<<format 4\frac{9}{25} \\ perc>>', 'format', 'mix -> perc'),
    (r'<<format 0,8 \\ perc>>', 'format', 'dec -> perc'),
    (r'<<format 41,5 \\ mix>>', 'format', 'dec -> mix'),
    (r'<<simplify (x^2 - y^2) : (x - y) \\ x=5 \\ y=3>>', 'simplify', 'подстановка в выражение'),
    (r'<<simplify \frac{6}{25} * (\frac{11}{15} - \frac{9}{20})>>', 'simplify', 'арифметика с дробями'),
    (r'<<simplify y = x^{- 2} \\ x = 0,0625 \\ y = b>>', 'simplify', 'подстановка в уравнение или неравенство'),
    (r'<<simplify \frac{2 + x - x^2}{2 - 5 x + 3 x^2} + \frac{10x}{3x - 2}>>', 'simplify', 'упрощение рац. выражений'),
    (r'<<simplify - 0,2a^2⋅b^3⋅(- 5a^3 b^2)^2>>', 'simplify', 'многочлены'),
    (r'<<simplify (2n + 1)^2 + (2n^2 + 2n)^2 = (2n^2 + 2n + 1)^2>>', 'simplify', 'уравнение или неравенство'),
    (r'<<simplify (1 \frac{1}{6})^9 * (\frac{6}{7})^{10}>>', 'simplify', 'арифметика со степенями'),
    (r'<<simplify \frac{3}{10} * (3\frac{9}{14} - 1\frac{10}{21} + 1\frac{1}{6})>>', 'simplify',
     'много арифметики чисел'),
    (r'<<simplify 295361 + 475829>>', 'simplify', 'сложение 2 чисел'),
    (r'<<simplify (140 - 12,32) : 42 + 3,1516>>', 'simplify', 'арифметика без дробей и степеней'),
    (r'<<simplify 199,26 : 0,82>>', 'simplify', 'арифметика 2 чисел'),
    (r'<<simplify \frac{36ab}{17c} : \frac{21b}{34c}>>', 'simplify', 'сокращение произведений'),
    (r'<<simplify \sqrt{\frac{81}{100}}>>', 'simplify', 'корни'),
    (r'<<solve 6u - 5v = - 38, \\ 2u + 7v = 22>>', 'solve', 'система двух линейных'),
    (r'<<solve \frac{1}{49}m^2 - 1 = 0>>', 'solve', 'квадратное x² = c'),
    (r'<<solve \frac{x}{3} + \frac{x}{4} < 7 \\ 1 - \frac{x}{6} > 0>>', 'solve', 'двойное неравенство'),
    (r'<<solve (2x - 5)(x + 2) = 18>>', 'solve', 'квадратное с дискриминантом'),
    # (r'<<solve (a^2 + 7a - 8)x = a^2 + 16a + 64>>', 'solve', 'линейное с параметром'),  # хз, что в arc'е
    (r'<<solve 1376 : (34 - x)=86>>', 'solve', 'сводящееся к линейному домножением'),
    (r'<<solve x^{10}= - 1>>', 'solve', 'какое-то непонятное уравнение'),
    (r'<<solve 2,9 x - 1,1 x = 5,04>>', 'solve', 'простое линейное уравнение'),
    (r'<<solve 4 - x(x + 8)=11 - x^2>>', 'solve', 'сводящееся к линейному сокращением'),
    # (r'<<solve 80 : x - 80 : (x + 16) = \frac{1}{6}>>', 'solve', 'сводящееся к квадратному'),  # хз, что в arc'е
    (r'<<solve x^3 - x = 0>>', 'solve', 'кубическое уравнение'),
    (r'<<solve |x| < 85>>', 'solve', 'неравенство с модулем'),
    (r'<<solve - 0,72 : | x | = - 0,9>>', 'solve', 'уравнение с модулем'),
    (r'<<solve \frac{5 - 2y}{12} \lt 1 - 6y>>', 'solve', 'линейное неравенство'),
    (r'<<solve ax^2 - (a + 1)x + 1 = 0>>', 'solve', 'квадратное с параметром'),
    (r'<<solve x^4 - 29x^2 + 100 = 0>>', 'solve', 'иные уравнения степении ⩾ 3'),
    (r'<<solve l^2 - 4 < 0>>', 'solve', 'квадратное неравенство'),
    (r'<<solve \sqrt{x} = - 3>>', 'solve', 'уравнения с корнями'),
    (r'<<solve (x - 1)(x - 9) = 0>>', 'solve', 'разложенное'),
    (r'<<solve 1 - 6x < 19 \\ 4x - a < 6>>', 'solve', 'система неравенств двух и более переменных'),
    (r'<<solve \frac{1}{6} x^2 - 5 x=0>>', 'solve', 'квадратное x² + bx = 0'),
    (r'<<units 3000000c \\ сутки \\ ч \\ мин>>', 'units', 'в две+ единицы'),
    (r'<<units 300000 км / с \\ м / с>>', 'units', 'скорости'),
    (r'<<units 16 км 527 м + 37 км 783 м>>', 'units', 'сложение'),
    (r'<<units (360 г) : (5,4 кг)>>', 'units', 'деление'),
    (r'<<units 5 мм \\ дм>>', 'units', 'преобразование в один тип'),
    (r'<<units 8 т 6 ц 25 кг - (4 т 8 ц 74 кг)>>', 'units', 'разность'),
    (r'<<units 9,701 м \\ км>>', 'units', 'нецелое число'),
    (r'<<units 12 ч 24 мин - (9 ч 18 мин)>>', 'units', 'преобразование времени'),
    (r'<<units (3 т 5 ц 65 кг) * 8>>', 'units', 'умножение'),
    (r'<<units 26 м 976 мм \\ м>>', 'units', '⩾две единицы в одну'),
    (r'<<units 4 м^3 \\ дм^3>>', 'units', 'единицы измерения со степенями'), ]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (expr, solver, verdict) in enumerate(cases):
        def test_math_classification(self, expr=expr, solver=solver, verdict=verdict):
            res = self.worker.solver(expr, timeout=3)
            math_subtype = mathsolvers.classify_math(solver, expr, res)
            self.assertEqual(str(math_subtype), verdict)

        test_math_classification.__name__ = tests_wrapper.tnesc(f'test_math_classification_{i + 1:03}: {expr}')
        setattr(Test, test_math_classification.__name__, test_math_classification)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
