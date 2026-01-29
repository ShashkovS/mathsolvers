# flake8: noqa: E501
from mathsolvers import solver, to_text, embed_solvers, pprint, parse, lat, hum  # noqa: F401
from mathsolvers.sympy_stuff.utils import srepr

cases = [
    # Базовые случаи
    (r"2/ab", r"2/(a*b)"),
    (r"22/36xy", r"22/(36xy)"),
    (r"2/a(b+c)", r"2/(a*(b+c))"),
    (r"ab/ab", r"(a*b)/(a*b)"),
    (r"abc/abc", r"(a*b*c)/(a*b*c)"),
    (r"abcd/abcd", r"(a*b*c*d)/(a*b*c*d)"),
    (r"2a^2b/a^2bc^3", r"2*a**2*b/(a**2*b*c**3)"),

    # Многосимвольные выражения
    (r"3abc/4 d e f", r"(3*a*b*c)/(4*d*e*f)"),
    (r"a/bc", r"a/(b*c)"),
    (r"abcd/efgh", r"(a*b*c*d)/(e*f*g*h)"),

    # Степени и составные выражения
    (r"x^2y^3/z^4w^5", r"(x**2*y**3)/(z**4*w**5)"),
    (r"a^2b^3/c^4d^5", r"a**2*b**3/(c**4*d**5)"),
    (r"(ab)^2/cd", r"(a*b)**2/(c*d)"),

    # Скобки в знаменателе
    (r"3/(ab)(c+d)", r"3/(a*b*(c + d))"),
    (r"(a+b)/cd(e+f)", r"(a + b)/(c*d*(e + f))"),
    (r"2/ab(c+d)", r"2/(a*b*(c + d))"),

    # Комбинированные операции
    # (r"2/ab * cd/ef", r"(2/(a*b))*(c*d/(e*f))"),
    (r"ab/cd + ef/gh", r"(a*b)/(c*d) + (e*f)/(g*h)"),
    # (r"a/b c/d + e/f g/h", r"(a/b)*(c/d) + (e/f)*(g/h)"),

    # Числовые коэффициенты
    (r"2ab/3cd", r"(2*a*b)/(3*c*d)"),
    (r"4a^2b/5c^3d", r"(4*a**2*b)/(5*c**3*d)"),
    (r"5^3xy/6^3zt", r"(5^3*x*y)/(6^3*z*t)"),

    # Множественные деления
    # (r"a/bc/d", r"a/(b*c)/d"),
    # (r"a/b/cd", r"(a/b)/(c*d)"),
    # (r"a/b/c/d", r"((a/b)/c)/d"),

    # Смешанные умножения
    (r"a*b/c*d", r"(a*b)/c*d"),
    (r"ab/cd*ef", r"(a*b)/(c*d)*e*f"),

    # Пробелы в выражении
    (r"2/ a b", r"2/(a*b)"),
    (r"ab / cd", r"(a*b)/(c*d)"),
    (r"2 / ab c", r"2/(a*b*c)"),

    # Вложенные дроби
    (r"a/(b/cd)", r"a/(b/(c*d))"),
    (r"(a/bc)/(d/ef)", r"(a/(b*c))/(d/(e*f))"),

    # Сложные комплексные выражения
    (r"2a(b+c)/3d(e+f)", r"2*a*(b + c)/(3*d*(e + f))"),
    (r"(ab+cd)/(ef+gh)", r"(a*b + c*d)/(e*f + g*h)"),
    (r"sin(ab)/cos(cd)", r"sin(a*b)/cos(c*d)"),
]


for expr, _ in cases:
    p = parse(expr)
    print(f'{expr=:<20}parsed={hum(p):<30}repr={srepr(p):<70} need {hum(parse(_))}')
exit()
# print(lat(parse('-x^2 - 4x - 4')))
# print(lat(parse('1/(-x^2)')))
# print(hum(parse('-x^2')))
# print(lat(parse('pcnt')))
# print(lat(parse('xx')))
# exit()

exprs = [
    # (r'<<simplify $\frac{18^n}{2^(n+1) \cdot 3^(2n-1)}>>', r''),
    # (r'<<simplify $\frac{14^(n-1) \cdot 21^(n+1)}{49^n \cdot 6^n }$>>', r''),
    # (r'<<simplify - d \\ d = - 6\frac{5}{11}>>', ''),
    # (r'<<solve  $x+2=\frac{15}{4x+1}$>>', '$x = -\frac{13}{4}; x = 1$'),
    # (r'<<solve  $\frac{2 x+16}{x+3}-\frac{1-3 x}{x+3}=0$>>', r''),
    # (r'<<solve 2*(3-8) = 5x + 0,2>>', r''),
    # (r'<<solve  $\frac{x^2-4}{4x}$=$\frac{3x-2}{2x}$>>', r'$x = 6$'),
    # (r'<<units 49дм - 324см + 1м\\ дм >>', r''),
    # (r'<<units 49м^2 - 324см^2 + 1ар \\ дм^2 >>', r''),
    # (r'<<units 49м^3 - 324см^3 - 1л \\ дм^3 >>', r''),
    # (r'<<units 49м^3 - 324см^3 \\ л >>', r''),
    # (r'<<units 49м/c - 324м/с \\ м/с >>', r''),
    # (r'<<units 1 ч + 1 мин + 1 с \\ мин >>', r''),
    # (r'<<units 1 ч + 1 мин + 1 с  >>', r''),
    # (r'<<units 4км 238м - (2км 520м)>>', r''),
    # (r'<<units 4.25км 238м - (2км 520м)>>', r''),
    # (r'<<units 4.25км 238м - (5км 520м)>>', r''),
    # (r'<<units 4.25км 238м - (5км 420м)>>', r''),
    # (r'<<units 4км 238мм - (2км 520мм)>>', r''),
    # (r'<<units 2,34 дм - 18 см \\ дм>>', r''),
    # (r'<<units 64 м 45 см - (27 м 86 см)>>', r'$36 м \  59 см$'),
    # (r'<<units 76 м 49 см + 41 м 58 см>>', r'$118 м \  7 см$'),
    # (r'<<units $\frac{11}{15}$ ч $\cdot 7$>>', r'$5 ч \  8 мин$'),
    # (r'<<units (8 м) : (1 км)>>', r''),
    # (r'<<simplify -2^{m-1} >>', r''),  # виснет
    # (r'<<simplify 2^{m} - 2^{m-1} >>', r''),  # виснет
    # (r'<<simplify 2^{m} \cdot 3^{n-1} - 2^{m-1} \cdot 3^{n}>>', r''),  # виснет
    # (r'<<simplify \frac{2^{m} \cdot 3^{n-1} - 2^{m-1} \cdot 3^{n}}{2^{m} \cdot 3^{n}}>>', r''),  # виснет
    # (r'<<simplify $\frac{18^n}{2^(n+1) \cdot 3^(2n-1)}>>', r''),
    # (r'<<calc (7,6 - 0,8) - (7,6 \cdot 0,8)>>', r''),
    # (r'<<simplify 2*(-1)>>', r''),
    # (r'<<simplify (1 + 2)>>', r''),
    # (r'<<simplify 2 \cdot (1 \frac{1}{3} + 3 \frac{5}{3})>>', r''),
    # (r'<<simplify  x - 0,2x >>', r''),
    # (r'<<simplify (-4x) / (-4) >>', r''),
    # (r'<<solve 36:(x-2)=4>>', r''), # виснет
    # (r'<<simplify ((1 1/5 : (17/40 + 0,6 - 0,005))*1,7):(5/6+1 1/3 - 1 23/30)+(4,75+7 1/2):(33 : (4 5/7)) : 0,25>>', r''),
    # (r'<<solve x^2-1,6x-0,36=0>>', r''),
    # (r'<<compare 600 - (25 * 4 + 28 * 5 - 120 : 2) : 6 - (36 : 18 + 510 : 170) * 20 > 107>>', r''),
    # (r'<<solve 3x > 40,8 \\ 5x - a < 0>>', r''),
    # (r'<<simplify |2 x - 6| - 2 x при x=2>>', r''),
    # (r'<<simplify 72 : b + 13 \\ b = 3>>', r''),
    # (r'<<format 2/3 \\ dec >>', r''),
    # (r'<<simplify  0,6y - 0,3(y- 4)  >> ', r''),
    # (r'<<solve x=2 >> ', r''),
    # (r'<<simplify $12\\text{ дм}^3 6\\text{ см}^3$>>', r''),
    # (r'<<simplify 0,009 * 12>>', r''),
    # (r'<<simplify 2+2>>', r''),
    # (r'<<solve  - x/5 + 1= 0 >>', r''),
    # (r'<<solve $(x-3)^{2}=7$>>', r''),
    # (r'<<simplify \frac{7}{8} - \frac{3}{16}>>', r''),
    # (r'<<solve \frac{2,5}{6,8} = \frac{1,5}{у}>>', r''),
    # (r'<<solve $\frac{4 - x}{4x - 3} = \frac{2x - 2}{7 - x}$>>', r''),
    # (r'<<solve $\frac{105}{y}$ = 7>>', r''),
    # (r'<<solve $1,6x^2=3x$>>', r''),
    # (r'<<solve $\frac{4 - x}{4x - 3} = \frac{2x - 2}{7 - x}$>>', r''),
    # (r'<<solve 3 + \dfrac{x-1}{3} = x >>', r''),
    (r'<<solve (54 x + 22) \cdot 315 = 23940>>', r''),
    # (r'', r''),
]

# print(mathsolvers.solvers.simplification.step_by_step_and_res('((1 1/5 : (17/40 + 0,6 - 0,005))*1,7):(5/6+1 1/3 - 1 23/30)+(4,75+7 1/2):(33 : (4 5/7)) : 0,25'))
# exit()

to_fix_bugs_exprs = [
    (r'', ''),  #
    (r'<<simplify (3 + (x-1)/3)*3 >>', ''),  # Чить с третюшками
    (r'<<solve \frac{4}{x} < 4>>', ''),  # Нельзя неравенство домножать на x
    (r'<<solve \frac{12 - 7x}{42} \ge 0>>', ''),  # упростим левую часть уравнения, хотя тут неравенство
    (r'<<simplify \frac{9}{11} + 0>>', ''),  # с нулём криво отрабатывает
    (r'<<simplify 1 −(x−5)(x+5) >>', ''),  # Мутный шаг с минусом
    (r'<<solve  n : 17 = 1>>', ''),  # Дичь с делением в превом шаге
    (r'<<simplify 10! >>', ''),  # факториал съедается
    (r'<<simplify ((-2)⁴)³ = (2⁴)³  >>', ''),  # а-а-а-а-а!!
    (r'<<solve (2 x - 3)^2=25>>', 'нужно решать без дискриминанта'),  #
    (r'100см и 1м', ''),  # не должно парситься
    (r'4;0,25', ''),  # не должно парситься
    (r'$1\in\left|7\right|$', ''),  # не должно парситься
    (r'a) $936 - 579$  ', ''),  # парсить пункты
    (r'$\begin{cases}-73y-2y>2-102\\11y-y\ge1-81\end{cases}$', ''),  # не парсится система

    (r'0/0', ''),  # парсится в nan
    (r'$\frac{3}{7}\div1+\frac{1}{14}=0,4\div\left(4-y\right)$', ''),  # парсится в True
    (r'436$\sqrt[3]{}476+8^2+\left|1\right|$', r''),  # не должен парситься
    (r'<<simplify $6\frac{1}{5}\times4$ >>', r''),  # не парсится
    (r'<<simplify 2 + 2 = 4 >>', r''),  # Лишние доллары
    (r'<<simplify -7 + (-1)*3 >>', r''),  # треш-формулировка
    (r'<<simplify 2 \cdot (1 \frac{1}{3} + 3 \frac{5}{3})>>', r''),  # Какая-то дичь в процессе упрощения
    (r'<<simplify  3x + 1,5y - 0,2x - 10y + 1,7x>>', r''),  # Дичь с преобразованиями типа туда-обратно
    (r'<<simplify  x - 0,2x >>', r''),  # Дичь с преобразованиями типа туда-обратно
    (r'<<simplify - x \cdot(-6)   \\ x = 3>>', ''),  # дичь с минусом
    (r'<<solve \frac{4}{x} < 4>>', r''),
    (r'<<simplify 2*(-5)>>', r''),  # Дичь с перекидыванием минуса
    (r'<<simplify 5 – 4 * (-2) >>', r''),  # Дичь с перекидыванием минуса
    (r'<< simplify 5 – 4b \\ b = -2 >>', r''),
    (r'<<units (32 км^2 81 гa 7 м^2) : (8 км^2 21 м^2) \\ а>>', r''),  # а-а-а!
    (r'<<units 4км 238м - (2км 520м)>>', r''),
    (r'<<units (12 м) : (1,8 км)>>', r''),  # немного дичь с дробями
    (r'<<units 1.123456т + 1.67кг >>', r''),  # 167/100кг.
    (r'<<simplify 5,4a - 3,9a \\ a = 0,26>>', r''),  # дичь-шаг
    (r'<<simplify - d \\ d = - 6\frac{5}{11}>>', r''),  # треш-шаги
    (r'<<compare 2,35 га \\ 235 а>>', r''),  # TODO
    (
        r'<<solve \frac{30}{x} - \frac{30}{y} = 1 \\ (\frac{90 - x}{x + 10} = \frac{90}{y})>>',
        r'',
    ),  # не работает из-за скобок
    (r'<<compare 45 \\ 4500 \\ 045 \\ 450 \\ 45000 \\ reverse>>', r''),  # парсинг ведущих нулей
    (r'<<solve 40 + \dfrac{x-10}{3}+\dfrac{x-30}{4} = x >>', r''),  # всё же домножать бы...
    (r'<<solve 228:x=12 >>', r''),  # Не хватает скобок после домножения на x в решении
    (r'<<simplify -8-1/3 >>', r''),  # 8 0/1
    (r'<<simplify 0,5 + 2 * 3/4 >>', r''),  # дичь шаги
    (r'<<simplify 2.0 *(3 1/4) >>', r''),  # дичь с промежуточной дробью
]

for i, (expr, ans) in enumerate(exprs):
    print(expr.replace('<', '&lt;').replace('>', '&gt;'))
    # solver(expr)
    # print(to_text(solver(expr)))
    pprint(solver(expr))
    # print(f'{i:>4}/{len(exprs)}: {expr=}')
    # print(expr.replace('<<', '$< <$').replace('>>', '$> >$'), file=f)
    # try:
    #     res = await solver_async(expr)
    # except Exception as e:
    #     print(e)
    #     continue
    # print(to_text(json.loads(res)), file=f)
