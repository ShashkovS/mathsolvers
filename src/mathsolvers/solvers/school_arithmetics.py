import dataclasses
import math

import sympy

from mathsolvers.solvers_stuff import classes
from mathsolvers.sympy_stuff import utils

__all__ = []

type_decoder = {
    utils.MRational: utils.NUM_STYLE.MIXED,
    utils.DRational: utils.NUM_STYLE.DECIMAL,
    utils.FRational: utils.NUM_STYLE.FRAC,
    sympy.Integer: utils.NUM_STYLE.FRAC,
    sympy.Rational: utils.NUM_STYLE.FRAC,
    sympy.core.numbers.One: utils.NUM_STYLE.FRAC,
    sympy.core.numbers.NegativeOne: utils.NUM_STYLE.FRAC,
    sympy.core.numbers.Zero: utils.NUM_STYLE.FRAC,
    sympy.core.numbers.Half: utils.NUM_STYLE.FRAC,
}


@dataclasses.dataclass
class ExtendedRational:
    f: sympy.core.numbers.Rational  # оригинальная дробь
    p: int  # модуль числителя
    q: int  # знаменатель
    sgn: int  # знак (+1/-1)
    wp: int  # целая часть смешанной дроби, 0, если дробь обыкновенная
    np: int  # числитель дробной части (просто числитель, если дробь обыкновенная)
    ns: utils.NUM_STYLE
    rwp: int  # реальная целая часть
    rnp: int  # остаток от деления числителя на знаменатель

    def __init__(self, f: sympy.core.numbers.Rational):
        self.f = f
        self.p, self.q = f.p, f.q
        self.sgn = 1 if self.p >= 0 else -1
        self.p = abs(self.p)

        self.ns = type_decoder.get(type(f))
        self.rwp, self.rnp = divmod(self.p, self.q)
        if isinstance(f, utils.MRational):
            self.wp, self.np = abs(f.wp), f.np
        elif self.q == 1:
            self.wp, self.np = abs(self.p), 0
        else:
            self.wp, self.np = 0, self.p
        if self.ns == utils.NUM_STYLE.MIXED and self.wp == 0:
            self.ns = utils.NUM_STYLE.FRAC

    def __str__(self):
        wps = '' if self.wp == 0 else f'{self.wp} '
        sgns = '' if self.sgn == 1 else '-'
        return f'{sgns}{wps}\\frac{{{self.np}}}{{{self.q}}}'


@dataclasses.dataclass
class ArithmState:
    expr: sympy.Expr
    steps: list[classes.Step]
    ans: sympy.Expr
    f1: sympy.core.numbers.Rational  # дробь
    f2: sympy.core.numbers.Rational
    r1: ExtendedRational
    r2: ExtendedRational
    or1: ExtendedRational  # or — исходные дроби без перестановки
    or2: ExtendedRational
    swapped: bool
    inverted: bool
    sol_codes: list[str]
    # Вспомогательное
    sum_p: int  # результат тупого сложения числителей
    sum_wp: int  # результат тупого сложения целых частей
    add_wp: int  # добавочная целая часть от сложения числителей
    nq: int  # итоговый знаменатель
    nwp: int  # итоговая целая часть результата
    nnp: int  # итоговый числитель дроби результата

    def __init__(
            self,
            expr: sympy.Expr,
            steps: list[classes.Step],
            f1: sympy.core.numbers.Rational,
            f2: sympy.core.numbers.Rational,
            ns: utils.NUM_STYLE = utils.NUM_STYLE.MIXED,
    ):
        self.expr = expr
        self.steps = steps
        self.ns = ns
        ans = expr.doit()
        # Это нужно, чтобы сократилась сократимая дробь
        self.ans = sympy.Rational(ans.p, ans.q)
        self.f1 = f1
        self.or1 = self.r1 = ExtendedRational(f1)
        self.f2 = f2
        self.or2 = self.r2 = ExtendedRational(f2)
        self.swapped = self.inverted = False
        self.sol_codes = []

    def add_step(self, action: str, solution: str, answer: str):
        self.steps.append(classes.Step(action=action, solution=solution, answer=answer))

    def swap(self):
        self.f1, self.f2 = self.f2, self.f1
        self.r1, self.r2 = self.r2, self.r1
        self.swapped = True


def arithmetics(expr: sympy.Expr, steps: list, ns) -> ArithmState:
    # # TODO Вот здесь кусок трешнячка, неоднозначного, поэтому пока не трогаем
    # if expr.func.__name__ == 'PDiv' and expr.args[0].is_Integer and expr.args[1].is_Integer:
    #     a, b = expr.args
    #     # Деление целого на целое
    #     dv, md = divmod(a, b)
    #     if md == 0:
    #         steps.append(classes.Step(
    #             action=f'Поделим ${a}$ на ${b}$',
    #             solution=f'',
    #             answer=f'${dv}$',
    #         ))
    if not expr.is_Add:
        return None
    fixed_args = []
    for arg in expr.args:
        if arg.is_Rational:
            fixed_args.append(arg)
        elif arg.is_Mul and len(arg.args) == 2 and arg.args[0] == -1 and arg.args[1].is_Rational:
            fixed_args.append(-arg.args[1])
        else:
            return None
    if len(fixed_args) != 2:
        return None
    expr = sympy.Add(*fixed_args, evaluate=False)
    # Добываем собственно слагаемые
    f1, f2 = fixed_args
    # Для дробей в 5-7 классах всегда предпочитаем смешанные дроби
    use_ns = utils.NUM_STYLE.MIXED
    s = ArithmState(expr, steps, f1, f2, use_ns)
    # Десятичные и периодические пока не трогаем
    if (
            s.r1.ns == utils.NUM_STYLE.DECIMAL
            or s.r2.ns == utils.NUM_STYLE.DECIMAL
            or isinstance(s.f1, utils.PRational)
            or isinstance(s.f2, utils.PRational)
    ):
        return None
    ###############################################################
    # Два целых
    whole1 = s.r1.q == 1
    mixed1 = not whole1 and s.r1.ns == utils.NUM_STYLE.MIXED and s.r1.wp != 0
    proper1 = not (whole1 or mixed1)
    whole2 = s.r2.q == 1
    mixed2 = not whole2 and s.r2.ns == utils.NUM_STYLE.MIXED and s.r2.wp != 0
    proper2 = not (whole2 or mixed2)
    # Здесь жесть отсюда:
    # https://docs.google.com/spreadsheets/d/1qwN5-fekTF1mQnQ7K3KkJo0VUVPr4bxk1iFLJ9Mo8BM/edit?gid=1989003043
    if whole1 and whole2:
        add_whole_and_whole(s)
    else:
        if s.r1.sgn == -1 and s.r2.sgn == -1:
            two_negative(s)
        elif s.r1.sgn == 1 and s.r2.sgn == -1 or s.r1.sgn == -1 and s.r2.sgn == 1:
            return None

        if whole1 and mixed2 or whole2 and mixed1:
            add_whole_and_mixed(s)
        elif whole1 and proper2 or whole2 and proper1:
            add_whole_and_proper(s)
        elif proper1 and proper2:
            add_proper_and_proper(s)
        elif mixed1 and mixed2:
            add_mixed_and_mixed(s)
        # остались proper + mixed
        else:
            add_proper_and_mixed(s)
        if s.inverted:
            minus_back(s)
    return s


def get_apple_word(n: int) -> str:
    if 11 <= n % 100 <= 19:
        return f"${n}$ яблок"
    last_digit = n % 10
    if last_digit == 1:
        return f"${n}$ яблоко"
    elif 2 <= last_digit <= 4:
        return f"${n}$ яблока"
    else:
        return f"${n}$ яблок"


def add_whole_and_whole(s: ArithmState):
    ##################################################################################################
    # Оба положительные
    s.sol_codes.append('add_whole_and_whole')
    if s.r1.sgn == 1 and s.r2.sgn == 1:
        ans = s.r1.p + s.r2.p
        # Есть случай с подсчётом "на пальцах"
        if 1 <= s.r1.p <= 9 and 1 <= s.r2.p <= 9:
            s.sol_codes.append('add_small_numbers_on_apples')
            apple_range = range(s.r1.p + 1, ans + 1)
            range_joined = ', '.join(map(str, apple_range))
            s.add_step(
                action=f'Пусть на столе лежат {get_apple_word(s.r1.p)}. '
                       f'Добавим к ним ещё {get_apple_word(s.r2.p)}. '
                       f'Посчитаем, сколько в сумме яблок получится.',
                solution=f'Возьмём {get_apple_word(s.r1.p)}. '
                         f'Добавим к ним {get_apple_word(s.r2.p)}. '
                         f'{get_apple_word(s.r1.p)} было, будем считать новые, получится: {range_joined}. '
                         f'В итоге получится {get_apple_word(ans)}. '
                         f'Значит, ${s.r1.p} + {s.r2.p} = {ans}$.',
                answer=f'${utils.lat(s.ans, s.ns)}$',
            )
        else:
            s.add_step(
                action=f'Сложим ${s.r1.p}$ и ${s.r2.p}$.',
                solution=f'Сложим ${s.r1.p}$ и ${s.r2.p}$, получится ${utils.lat(s.ans, s.ns)}$',
                answer=f'${utils.lat(s.ans, s.ns)}$',
            )
        return sympy.Integer(ans)
    ##################################################################################################
    # a - b
    elif s.r1.sgn == 1 and s.r2.sgn == -1:
        ans = s.r1.p - s.r2.p
        if ans >= 0:
            solution = f'Вычтем ${s.r2.p}$ из ${s.r1.p}$, получится ${ans}$'
        else:
            solution = (
                f'Так как ${s.r2.p}$ больше, чем ${s.r1.p}$, то чтобы вычесть ${s.r2.p}$ из ${s.r1.p}$, '
                f'мы вычтем ${s.r1.p}$ из ${s.r2.p}$ и возьмём результат со знаком минус. '
                f'Получится ${s.r1.p} - {s.r2.p} = -({s.r2.p} - {s.r1.p}) = {ans}$'
            )
        s.add_step(action=f'Вычтем ${s.r2.p}$ из ${s.r1.p}$.', solution=solution, answer=f'${ans}$')
        return sympy.Integer(ans)
    ##################################################################################################
    # -a + b
    elif s.r1.sgn == -1 and s.r2.sgn == 1:
        ans = s.r2.p - s.r1.p
        if ans >= 0:
            solution = f'Сложим $-{s.r1.p}$ и ${s.r2.p}$. Для этого из ${s.r2.p}$ вычтем ${s.r1.p}$, получится ${ans}$'
        else:
            solution = (
                f'Так как ${s.r1.p}$ больше, чем ${s.r2.p}$, то чтобы сложить $-{s.r1.p}$ и ${s.r2.p}$, '
                f'мы вычтем ${s.r2.p}$ из ${s.r1.p}$ и возьмём результат со знаком минус. '
                f'Получится $-{s.r1.p} + {s.r2.p} = -({s.r1.p} - {s.r2.p}) = {ans}$'
            )
        s.add_step(action=f'Сложим $-{s.r1.p}$ и ${s.r2.p}$.', solution=solution, answer=f'${ans}$')
        return sympy.Integer(ans)
    ##################################################################################################
    # -a - b
    else:
        s.add_step(
            action=f'Вычтем из $-{s.r1.p}$ число ${s.r2.p}$.',
            solution=(
                f'Вычтем из $-{s.r1.p}$ число ${s.r2.p}$. '
                f'Для этого сложим ${s.r1.p}$ и ${s.r2.p}$ и возьмём результат со знаком минус. '
                f'Получаем $-{s.r1.p} - {s.r2.p} = -({s.r1.p} + {s.r2.p}) = {utils.lat(s.ans, s.ns)}$'
            ),
            answer=f'${utils.lat(s.ans, s.ns)}$',
        )


def add_whole_and_mixed(s: ArithmState):
    s.sol_codes.append('add_whole_and_mixed')
    ##################################################################################################
    # Оба положительные
    if s.r1.sgn == 1 and s.r2.sgn == 1:
        # Сначала сделаем так, чтобы целым было первое
        if s.r1.q != 1:
            s.swap()
        add_nums_fill_fields(s)
        add_wholes_leave_fraction(s)
        if s.r2.np >= s.r2.q and s.r2.np % s.r2.q != 0:
            frac_part_to_mixed(s)
            frac_part_to_mixed_add_whole(s)
        elif s.r2.np >= s.r2.q and s.r2.np % s.r2.q == 0:
            frac_part_to_whole(s)
            frac_part_to_whole_add_whole(s)
        reduce_frac_mixed(s)
    ##################################################################################################
    # a - b
    elif s.r1.sgn == 1 and s.r2.sgn == -1 or s.r1.sgn == -1 and s.r2.sgn == 1:
        pass
    ##################################################################################################
    # -a - b
    else:
        pass


def add_whole_and_proper(s: ArithmState):
    s.sol_codes.append('add_whole_and_proper')
    ##################################################################################################
    # Оба положительные
    if s.r1.sgn == 1 and s.r2.sgn == 1:
        # Сначала сделаем так, чтобы целым было первое
        if s.r1.q != 1:
            s.swap()
        add_nums_fill_fields(s)
        if s.r2.p >= s.r2.q and s.r2.p % s.r2.q != 0:
            frac_to_mixed(s)
            remainder_and_add_wholes_leave_fraction(s)
        elif s.r2.p >= s.r2.q and s.r2.p % s.r2.q == 0:
            frac_part_to_whole(s)
            remainder_and_frac_part_to_whole_add_whole(s)
        elif s.r2.p < s.r2.q:
            addition_as_mixed(s)
        reduce_frac_mixed(s)
    ##################################################################################################
    # a - b
    elif s.r1.sgn == 1 and s.r2.sgn == -1 or s.r1.sgn == -1 and s.r2.sgn == 1:
        pass
    ##################################################################################################
    # -a - b
    else:
        pass


def add_proper_and_proper(s: ArithmState):
    s.sol_codes.append('add_proper_and_proper')
    ##################################################################################################
    # Оба положительные
    if s.r1.sgn == 1 and s.r2.sgn == 1:
        denom_same(s)
        if s.r1.q != s.r2.q:
            common_denom(s)
        add_nums_fill_fields(s)
        add_frac_same_denom(s)
        if s.sum_p >= s.r1.q and s.sum_p % s.r1.q != 0:
            frac_to_mixed_solo(s)
            reduce_frac_mixed(s)
        elif s.sum_p >= s.r1.q and s.sum_p % s.r1.q == 0:
            frac_to_whole(s)
        else:
            reduce_frac_solo(s)
    ##################################################################################################
    # a - b
    elif s.r1.sgn == 1 and s.r2.sgn == -1 or s.r1.sgn == -1 and s.r2.sgn == 1:
        pass
    ##################################################################################################
    # -a - b
    else:
        pass


def add_mixed_and_mixed(s: ArithmState):
    s.sol_codes.append('add_mixed_and_mixed')
    ##################################################################################################
    # Оба положительные
    if s.r1.sgn == 1 and s.r2.sgn == 1:
        denom_same_mixed(s)
        if s.r1.q != s.r2.q:
            common_denom_mixed(s)
        add_nums_fill_fields(s)
        add_wholes_add_frac(s)
        if s.sum_p >= s.r1.q and s.sum_p % s.r1.q != 0:
            frac_part_to_mixed(s)
            frac_part_to_mixed_add_whole(s)
        elif s.sum_p >= s.r1.q and s.sum_p % s.r1.q == 0:
            frac_part_to_whole(s)
            remainder_and_frac_part_to_whole_add_whole(s)
        reduce_frac_mixed(s)

    ##################################################################################################
    # a - b
    elif s.r1.sgn == 1 and s.r2.sgn == -1 or s.r1.sgn == -1 and s.r2.sgn == 1:
        pass
    ##################################################################################################
    # -a - b
    else:
        pass


def add_proper_and_mixed(s: ArithmState):
    s.sol_codes.append('add_proper_and_mixed')
    ##################################################################################################
    # Оба положительные
    if s.r1.sgn == 1 and s.r2.sgn == 1:
        # Сначала сделаем так, чтобы смешанным было первое
        if s.r2.wp != 0:
            s.swap()
        denom_same_mixed_frac(s)
        if s.r1.q != s.r2.q:
            common_denom_mixed_frac(s)
        add_nums_fill_fields(s)
        add_frac_leave_whole(s)
        if s.sum_p >= s.r1.q and s.sum_p % s.r1.q != 0:
            frac_part_to_mixed(s)
            frac_part_to_mixed_add_whole(s)
        elif s.sum_p >= s.r1.q and s.sum_p % s.r1.q == 0:
            frac_part_to_whole(s)
            remainder_and_frac_part_to_whole_add_whole(s)
        reduce_frac_mixed(s)

    ##################################################################################################
    # a - b
    elif s.r1.sgn == 1 and s.r2.sgn == -1 or s.r1.sgn == -1 and s.r2.sgn == 1:
        pass
    ##################################################################################################
    # -a - b
    else:
        pass


def add_frac_leave_whole(s: ArithmState):
    answer = f'${s.sum_wp} \\frac{{{s.sum_p}}}{{{s.nq}}}$'
    s.add_step(
        action=(
            f'Перепишем целую часть ${s.r1.wp}$ '
            f'и сложим дробные части $\\frac{{{s.or1.np}}}{{{s.or1.q}}}$ и $\\frac{{{s.or2.np}}}{{{s.or2.q}}}$. '
            f'Запишем результат как смешанное число (без знака плюс).'
        ),
        solution=(
            f'Сложим дробные части $\\frac{{{s.or1.np}}}{{{s.or1.q}}}$ и $\\frac{{{s.or2.np}}}{{{s.or2.q}}}$. '
            f'Чтобы сложить дроби с одинаковым знаменателем, сложим числители ${s.or1.np}$ и ${s.or2.np}$, '
            f'а знаменатель ${s.or2.q}$ перепишем без изменений. '
            f'Получается $\\frac{{{s.sum_p}}}{{{s.nq}}}$. '
            f'Перепишем целую часть, ${s.r1.wp}$, и результат сложения дробных частей, '
            f'$\\frac{{{s.sum_p}}}{{{s.nq}}}$, как смешанное число. '
            f'Получается {answer}.'
        ),
        answer=answer,
    )


def add_nums_fill_fields(s: ArithmState):
    s.nq = s.r2.q
    s.sum_p = s.r1.np + s.r2.np
    s.sum_wp = s.r1.wp + s.r2.wp
    s.add_wp, s.nnp = divmod(s.sum_p, s.nq)
    s.nwp = s.sum_wp + s.add_wp


def add_frac_same_denom(s: ArithmState):
    answer = f'$\\frac{{{s.sum_p}}}{{{s.r1.q}}}$'
    s.add_step(
        action='Сложим дроби с одинаковым знаменателем.',
        solution=(
            f'Чтобы сложить дроби с одинаковым знаменателем, '
            f'сложим числители ${s.r1.p}$ и ${s.r2.p}$, '
            f'а знаменатель ${s.r1.q}$ перепишем без изменений. '
            f'Получается {answer}.'
        ),
        answer=answer,
    )


def add_wholes_add_frac(s: ArithmState):
    answer = f'${s.sum_wp} \\frac{{{s.sum_p}}}{{{s.nq}}}$'
    s.add_step(
        action=(
            f'Сложим целые части ${s.r1.wp}$ и ${s.r2.wp}$ '
            f'и дробные части $\\frac{{{s.r1.np}}}{{{s.r1.q}}}$ и $\\frac{{{s.r2.np}}}{{{s.r2.q}}}$. '
            f'Запишем результат как смешанное число (без знака плюс).'
        ),
        solution=(
            f'Сложим целые части ${s.r1.wp}$ и ${s.r2.wp}$. '
            f'Получается ${s.sum_wp}$. '
            f'Сложим дробные части $\\frac{{{s.r1.np}}}{{{s.r1.q}}}$ и $\\frac{{{s.r2.np}}}{{{s.r2.q}}}$. '
            f'Чтобы сложить дроби с одинаковым знаменателем, '
            f'сложим числители ${s.r1.np}$ и ${s.r2.np}$, а знаменатель перепишем без изменений. '
            f'Получается $\\frac{{{s.sum_p}}}{{{s.nq}}}$. '
            f'Перепишем результат сложения целых частей, ${s.sum_wp}$, '
            f'и дробных частей, $\\frac{{{s.sum_p}}}{{{s.nq}}}$, как смешанное число. '
            f'Получается {answer}.'
        ),
        answer=answer,
    )


def add_wholes_leave_fraction(s: ArithmState):
    answer = f'${s.sum_wp} \\frac{{{s.sum_p}}}{{{s.nq}}}$'
    if s.swapped:
        a1, a2 = s.r2.wp, s.r1.wp
    else:
        a1, a2 = s.r1.wp, s.r2.wp
    s.add_step(
        action='Сложим целые числа и перепишем дробную часть смешанного числа без изменений.',
        solution=(
            f'Сложим ${a1}$ и ${a2}$, дробь $\\frac{{{s.r2.np}}}{{{s.r2.q}}}$ перепишем без изменений. '
            f'Получается {answer}.'
        ),
        answer=answer,
    )


def addition_as_mixed(s: ArithmState):
    answer = f'${s.r1.rwp} \\frac{{{s.r2.p}}}{{{s.r2.q}}}$'
    s.add_step(
        action='Запишем сложение в виде смешанного числа.',
        solution=(
            f'Чтобы записать сложение в виде смешанного числа, '
            f'перепишем целое ${s.r1.rwp}$ и дробь $\\frac{{{s.r2.p}}}{{{s.r2.q}}}$ без знака плюс. '
            f'Получается {answer}.'
        ),
        answer=answer,
    )


def after_actions_frac(s: ArithmState):
    s.add_step(
        action=f'После преобразования получилось ${1} - {1}$. Вычтем дробь из смешанного числа.',
        solution=(
            f'Чтобы из ${1}$ вычесть ${1}$, запишем ${1}$ как сумму ${1}$ и ${1}$. '
            f'Представим единицу как дробь со знаменателем ${1}$. Это ${1}$. '
            f'Теперь вычислим выражение с дробями: ${1} + {1} - {1}$. '
            f'Чтобы выполнить это выражение, '
            f'выполним операции с числителями и перепишем знаменатель без изменений. '
            f'Получается ${1}$. Соберём что осталось: мы не трогали ${1}$, '
            f'и в результате вычитания получилось ${1}$. '
            f'Итог запишем как смешанное число: ${1}$.'
        ),
        answer='',
    )


def after_actions_minus(s: ArithmState):
    s.add_step(
        action=(
            f'После преобразования получилось вычитание ${1} - {1}$. '
            f'Второе число в выражении больше чем первое. '
            f'Вынесем минус за скобки чтобы вычитать из большего меньшее.'
        ),
        solution=f'Напишем минус вне скобок, а внутри скобок поменяем числа местами. Получится $-({1} - {1})$.',
        answer='',
    )


def after_actions_minus_wholes_and_fractions(s: ArithmState):
    s.add_step(
        action=(
            'Теперь ненадолго забудем про минус и будем работать только с выражением в скобках. '
            'Вычтем целые части и дробные части смешанных чисел.'
        ),
        solution=(
            f'Вычтем целые части: ${1}$ и ${1}$, получается ${1}$. '
            f'Вычтем из дробной части ${1}$ вторую дробную часть ${1}$. '
            f'Для этого вычтем из первого числителя второй и перепишем знаменатель. '
            f'Получится ${1}$. Запишем, что получилось: ${1}$.'
        ),
        answer='',
    )


def after_actions_wholes(s: ArithmState):
    s.add_step(
        action=(
            f'После преобразования получилось вычитание: ${1} - {1}$. '
            f'Вычтем из ${1}$ сначала целую часть уменьшаемого $({1})$. '
            f'Перепишем выражение как получившееся смешанное число минус дробная часть вычитаемого.'
        ),
        solution=(
            f'Вычтем из ${1}$ целую часть уменьшаемого $({1})$. '
            f'Чтобы вычесть целое число из смешанного, нужно вычесть целые, а дробную часть переписать без изменений. '
            f'Получается ${1}$. Перепишем выражение как получившееся смешанное число минус дробная часть вычитаемого. '
            f'Получается ${1} - {1}$.'
        ),
        answer='',
    )


def after_actions_wholes_and_fractions(s: ArithmState):
    s.add_step(
        action=(
            f'После преобразования получилось вычитание ${1} - {1}$. '
            f'Вычтем целые части и дробные части смешанных чисел.'
        ),
        solution=(
            f'Вычтем целые части: ${1}$ и ${1}$, получается ${1}$. '
            f'Вычтем из дробной части ${1}$ вторую дробную часть ${1}$. '
            f'Для этого вычтем из первого числителя второй и перепишем знаменатель. '
            f'Получится ${1}$. Запишем, что получилось: ${1}$.'
        ),
        answer='',
    )


def calc_common_denom(a: int, b: int):
    if a % b == 0:
        return a, 1, a // b
    if b % a == 0:
        return b, b // a, b
    return a * b, b, a


def common_denom(s: ArithmState):
    s.nq = s.r1.q * s.r2.q
    answer = f'$\\frac{{{s.r1.p * s.r2.q}}}{{{s.nq}}} + \\frac{{{s.r2.p * s.r1.q}}}{{{s.nq}}}$'
    s.add_step(
        action='Приведём дроби к одному знаменателю и перепишем сумму в виде дробей с одинаковым знаменателем.',
        solution=(
            f'Чтобы найти общий знаменатель, надо перемножить знаменатели. '
            f'${s.r1.q} \\cdot {s.r2.q}$ — это ${s.nq}$. '
            f'Теперь приведём обе дроби к знаменателю ${s.nq}$. '
            f'У ${s.f1}$ надо и числитель, и знаменатель умножить на ${s.r2.q}$. '
            f'Получается $\\frac{{{s.r1.p * s.r2.q}}}{{{s.nq}}}$. '
            f'У ${s.f2}$ надо и числитель, и знаменатель умножить на ${s.r1.q}$. '
            f'Получается $\\frac{{{s.r2.p * s.r1.q}}}{{{s.nq}}}$. '
            f'Запишем сумму: {answer}.'
        ),
        answer=answer,
    )
    s.r1.p *= s.r2.q
    s.r1.np *= s.r2.q
    s.r1.rnp *= s.r2.q
    s.r2.p *= s.r1.q
    s.r2.np *= s.r1.q
    s.r2.rnp *= s.r2.q
    s.r1.q = s.r2.q = s.nq


def common_denom_mixed(s: ArithmState):
    s.nq = s.r1.q * s.r2.q
    nf1 = f'\\frac{{{s.r1.np * s.r2.q}}}{{{s.r1.q * s.r2.q}}}'
    nf2 = f'\\frac{{{s.r2.np * s.r1.q}}}{{{s.r2.q * s.r1.q}}}'
    answer = f'${s.r1.wp} {nf1} + {s.r2.wp} {nf2}$'
    s.add_step(
        action=(
            'Приведём дробные части к одному знаменателю. '
            'Перепишем пример как сумму смешанных чисел, где дробные части имеют одинаковый знаменатель.'
        ),
        solution=(
            f'Чтобы найти общий знаменатель, надо перемножить знаменатели. '
            f'${s.r1.q} \\cdot {s.r2.q}$ — это ${s.nq}$. '
            f'Теперь приведём обе дроби к знаменателю ${s.nq}$. '
            f'У $\\frac{{{s.r1.np}}}{{{s.r1.q}}}$ надо и числитель, и знаменатель умножить на ${s.r2.q}$. '
            f'Получается ${nf1}$. '
            f'Целая часть была ${s.r1.wp}$, поэтому перепишем первое слагаемое как ${s.r1.wp} {nf1}$. '
            f'У $\\frac{{{s.r2.np}}}{{{s.r2.q}}}$ надо и числитель, и знаменатель умножить на ${s.r1.q}$. '
            f'Получается ${nf2}$. '
            f'Целая часть была ${s.r2.wp}$, поэтому перепишем второе слагаемое как ${s.r2.wp} {nf2}$. '
            f'Запишем сумму: ${s.r1.wp} {nf1} + {s.r2.wp} {nf2}$.'
        ),
        answer=answer,
    )
    s.r1.p *= s.r2.q
    s.r1.np *= s.r2.q
    s.r1.rnp *= s.r2.q
    s.r2.p *= s.r1.q
    s.r2.np *= s.r1.q
    s.r2.rnp *= s.r2.q
    s.r1.q = s.r2.q = s.nq


def common_denom_mixed_frac(s: ArithmState):
    s.nq = s.r1.q * s.r2.q
    nf1 = f'$\\frac{{{s.or1.np * s.or2.q}}}{{{s.or1.q * s.or2.q}}}$'
    nf2 = f'$\\frac{{{s.or2.np * s.or1.q}}}{{{s.or2.q * s.or1.q}}}$'
    wps1 = '' if s.or1.wp == 0 else f'${s.or1.wp}$ '
    wps2 = '' if s.or2.wp == 0 else f'${s.or2.wp}$ '
    answer = f'${wps1}{nf1} + {wps2}{nf2}$'
    mixed_sol = (
        f'У $\\frac{{{s.r1.np}}}{{{s.r1.q}}}$ надо и числитель, и знаменатель умножить на ${s.r2.q}$. '
        f'Получается $\\frac{{{s.r1.np * s.r2.q}}}{{{s.nq}}}$. '
        f'Целая часть была ${s.r1.wp}$, '
        f'поэтому перепишем смешанную дробь как ${s.r1.wp} \\frac{{{s.r1.np * s.r2.q}}}{{{s.nq}}}$. '
    )
    frac_sol = (
        f'У $\\frac{{{s.r2.np}}}{{{s.r2.q}}}$ надо и числитель, и знаменатель умножить на ${s.r1.q}$. '
        f'Получается $\\frac{{{s.r2.np * s.r1.q}}}{{{s.nq}}}$. '
    )
    part1, part2 = mixed_sol, frac_sol
    if s.swapped:
        part1, part2 = part2, part1
    s.add_step(
        action=(
            'Приведём дробные части к одному знаменателю. '
            'Перепишем пример как сумму смешанного числа и дроби, '
            'где у обоих слагаемых одинаковый знаменатель.'
        ),
        solution=(
            f'Чтобы найти общий знаменатель, надо перемножить знаменатели. '
            f'${s.or1.q} \\cdot {s.or2.q}$ — это ${s.nq}$. '
            f'Теперь приведём обе дроби к знаменателю ${s.nq}$. '
            f'${part1}{part2}$'
            f'Ответ {answer}.'
        ),
        answer='',
    )
    s.r1.p *= s.r2.q
    s.r1.np *= s.r2.q
    s.r1.rnp *= s.r2.q
    s.r2.p *= s.r1.q
    s.r2.np *= s.r1.q
    s.r2.rnp *= s.r2.q
    s.r1.q = s.r2.q = s.nq


def denom_same(s: ArithmState):
    if s.r1.q == s.r2.q:
        common = 'одинаковые'
        answer = 'да'
    else:
        common = 'разные'
        answer = 'нет'
    s.add_step(
        action='У этих дробей одинаковые знаменатели?',
        solution=(
            f'У дроби числитель над дробной чертой, а знаменатель — под. '
            f'Знаменатели у этих дробей ${s.r1.q}$ и ${s.r2.q}$. '
            f'Значит, у них {common} знаменатели. Ответ — {answer}.'
        ),
        answer=f'{answer.title()}',
    )


def denom_same_mixed(s: ArithmState):
    if s.r1.q == s.r2.q:
        common = 'одинаковые'
        answer = 'да'
    else:
        common = 'разные'
        answer = 'нет'
    s.add_step(
        action='У дробных частей одинаковые знаменатели?',
        solution=(
            f'Дробные части у смешанных дробей $\\frac{{{s.r1.np}}}{{{s.r1.q}}}$ и $\\frac{{{s.r2.np}}}{{{s.r2.q}}}$. '
            f'У дроби числитель над дробной чертой, а знаменатель — под. '
            f'Знаменатели у этих дробей ${s.r1.q}$ и ${s.r2.q}$. '
            f'Значит, у них {common} знаменатели. Ответ — {answer}.'
        ),
        answer=f'{answer.title()}',
    )


def denom_same_mixed_frac(s: ArithmState):
    if s.r1.q == s.r2.q:
        common = 'одинаковые'
        answer = 'да'
    else:
        common = 'разные'
        answer = 'нет'
    s.add_step(
        action='В дробной части смешанного числа и у второго слагаемого одинаковые знаменатели?',
        solution=(
            f'Дробная часть смешанной дроби $\\frac{{{s.r1.np}}}{{{s.r1.q}}}$, '
            f'вторая дробь — $\\frac{{{s.r2.np}}}{{{s.r2.q}}}$. '
            f'У дроби числитель над дробной чертой, а знаменатель — под. '
            f'Знаменатели у них ${s.r1.q}$ и ${s.r2.q}$. '
            f'Значит, у них {common} знаменатели. Ответ — {answer}.'
        ),
        answer=answer,
    )


def first_fraction_to_mixed_subtr(s: ArithmState):
    s.add_step(
        action=(
            f'В дробной части вычитаемого ${1}$ числитель больше знаменателя. '
            f'Запишем дробную часть в виде смешанного числа и прибавим к целой части ${1}$.'
        ),
        solution=(
            f'Разделим ${1}$ на ${1}$ с остатком. '
            f'Частное равно ${1}$. Это целая часть. '
            f'Остаток равен ${1}$. Это числитель дробной части. '
            f'Получается ${1}$. Целая часть ${1}$ была ${1}$. '
            f'Чтобы записать вычитаемое как смешанное число, прибавим к целой части ${1}$ преобразованное число ${1}$. '
            f'Получится ${1}$.'
        ),
        answer='',
    )


def frac_part_to_mixed(s: ArithmState):
    answer = f'${s.add_wp} \\frac{{{s.nnp}}}{{{s.nq}}}$'
    s.add_step(
        action=(
            f'В дробной части $\\frac{{{s.sum_p}}}{{{s.nq}}}$ числитель больше знаменателя. '
            f'Переведём эту дробь в смешанное число.'
        ),
        solution=(
            f'Разделим ${s.sum_p}$ на ${s.nq}$ с остатком. Частное равно ${s.add_wp}$. Это целая часть. '
            f'Остаток равен ${s.nnp}$. Это числитель дробной части. Получается {answer}.'
        ),
        answer=answer,
    )


def frac_part_to_mixed_add_whole(s: ArithmState):
    answer = f'${s.nwp} \\frac{{{s.nnp}}}{{{s.nq}}}$'
    s.add_step(
        action=(
            f'Целая часть была ${s.sum_wp}$. '
            f'Мы перевели дробную часть в смешанное число и получили ${s.add_wp} \\frac{{{s.nnp}}}{{{s.nq}}}$. '
            f'Сложим целые числа и перепишем дробную часть смешанного числа без изменений.'
        ),
        solution=(
            f'Сложим ${s.sum_wp}$ и ${s.add_wp}$, дробь $\\frac{{{s.nnp}}}{{{s.nq}}}$ перепишем без изменений. '
            f'Получается {answer}.'
        ),
        answer=answer,
    )


def frac_part_to_whole(s: ArithmState):
    s.add_step(
        action=(
            f'В дробной части $\\frac{{{s.sum_p}}}{{{s.nq}}}$ числитель делится на знаменатель. '
            f'Запишем эту дробь как число'
        ),
        solution=f'Разделим ${s.sum_p}$ на ${s.nq}$. Получается ${s.add_wp}$.',
        answer=f'${s.add_wp}$',
    )


def frac_part_to_whole_add_whole(s: ArithmState):
    answer = f'${s.nwp}$'
    s.add_step(
        action=(
            f'Целая часть была ${s.sum_wp}$. '
            f'Мы перевели дробную часть в целое число и получили ${s.add_wp}$. '
            f'Сложим целые числа.'
        ),
        solution=(f'Сложим ${s.sum_wp}$ и ${s.add_wp}$. ' f'Получается {answer}.'),
        answer=answer,
    )


def frac_part_to_whole_subtract(s: ArithmState):
    s.add_step(
        action=(
            f'В дробной части вычитаемого ${1}$ числитель кратный знаменателю. '
            f'Запишем дробную часть в виде целого и прибавим к целой части ${1}$. '
            f'Перепишем всё вычитание с преобразованным вычитаемым.'
        ),
        solution=(
            f'В дробной части вычитаемого ${1}$ числитель делится на знаменатель. '
            f'Запишем дробную часть в виде целого и прибавим к целой части ${1}$. '
            f'Перепишем всё вычитание с преобразованным вычитаемым.'
        ),
        answer='',
    )


def frac_to_mixed(s: ArithmState):
    answer = f'${s.r2.rwp} \\frac{{{s.r2.rnp}}}{{{s.r2.q}}}$'
    s.add_step(
        action=(
            f'У дроби $\\frac{{{s.r2.p}}}{{{s.r2.q}}}$ числитель больше знаменателя. '
            f'Переведём эту дробь в смешанное число.'
        ),
        solution=(
            f'Разделим ${s.r2.p}$ на ${s.r2.q}$ с остатком. '
            f'Частное равно ${s.r2.rwp}$. '
            f'Это целая часть. '
            f'Остаток равен ${s.r2.rnp}$. '
            f'Это числитель дробной части. '
            f'Получается {answer}.'
        ),
        answer=answer,
    )


def remainder_and_add_wholes_leave_fraction(s: ArithmState):
    answer = f'${s.nwp} \\frac{{{s.nnp}}}{{{s.nq}}}$'
    if s.swapped:
        a1, a2 = s.f2, s.f1
    else:
        a1, a2 = s.f1, s.f2
    s.add_step(
        action=(
            f'Мы складывали ${a1}$ и ${a2}$. '
            f'Мы перевели дробь $\\frac{{{s.r2.p}}}{{{s.r2.q}}}$ в смешанное число '
            f'и получили ${s.r2.rwp} \\frac{{{s.r2.rnp}}}{{{s.r2.q}}}$. '
            f'Сложим ${s.r1.rwp}$ и ${s.r2.rwp} \\frac{{{s.r2.rnp}}}{{{s.r2.q}}}$. '
            f'Для этого сложим целые и перепишем дробную часть без изменений.'
        ),
        solution=(
            f'Сложим ${s.r1.rwp}$ и ${s.r2.rwp}$, дробь $\\frac{{{s.r2.rnp}}}{{{s.r2.q}}}$ перепишем без изменений. '
            f'Получается {answer}.'
        ),
        answer=answer,
    )


def frac_to_mixed_solo(s: ArithmState):
    answer = f'${s.nwp} \\frac{{{s.nnp}}}{{{s.nq}}}$'
    s.add_step(
        action=(
            f'У получившейся дроби числитель ${s.sum_p}$ больше знаменателя ${s.r2.q}$. '
            f'Переведём эту дробь в смешанное число.'
        ),
        solution=(
            f'Разделим ${s.sum_p}$ на ${s.r2.q}$ с остатком. '
            f'Частное равно ${s.nwp}$. '
            f'Это целая часть. '
            f'Остаток равен ${s.nnp}$. '
            f'Это числитель дробной части. '
            f'Получается {answer}.'
        ),
        answer=answer,
    )


def frac_to_whole(s: ArithmState):
    s.add_step(
        action=(
            f'У получившейся дроби ${s.sum_p}$ числитель делится на знаменатель ${s.r1.q}$. '
            f'Запишем эту дробь как число.'
        ),
        solution=f'Разделим ${s.sum_p}$ на ${s.r1.q}$. Получается ${s.nwp}$.',
        answer=f'${s.nwp}$',
    )


def include_negative(s: ArithmState):
    s.add_step(
        action='Теперь ненадолго забудем про минус и будем работать только с выражением в скобках. ......',
        solution=f'Выражение в скобках: ${1} + {1}$. .....',
        answer='',
    )


def minus_back(s: ArithmState):
    s.add_step(
        action='Ранее мы выносили минус за скобки. Чтобы получить ответ, запишем минус перед полученным числом.',
        solution=(
            f'На предыдущем шаге мы получили ${utils.lat(s.ans, s.ns)}$. '
            f'Запишем спереди минус. Получится $-{utils.lat(s.ans, s.ns)}$.'
        ),
        answer=f'$-{utils.lat(s.ans, s.ns)}$',
    )
    s.ans = -s.ans


def minus_mixed_minus_whole(s: ArithmState):
    s.add_step(
        action=(
            'Теперь ненадолго забудем про минус и будем работать только с выражением в скобках. '
            'Вычтем из целой части смешанного числа целое. Дробную часть перепишем без изменений.'
        ),
        solution=(
            f'Целая часть смешанного числа — ${1}$. Целое — ${1}$. Их разность — ${1}$. '
            f'Дробь ${1}$ перепишем без изменений. Получится ${1}$.'
        ),
        answer='',
    )


def one_minus_frac(s: ArithmState):
    s.add_step(
        action=f'После вычитания целых мы получили ${1}$. Осталось вычесть ${1}$.',
        solution=(
            f'Чтобы из ${1}$ вычесть ${1}$, представим единицу как дробь со знаменателем ${1}$. '
            f'Это ${1}$. Из ${1}$ вычтем ${1}$, получится ${1}$.'
        ),
        answer='',
    )


def parenthethese(s: ArithmState):
    s.add_step(
        action='Теперь ненадолго забудем про минус и будем работать только с выражением в скобках. ......',
        solution=f'Выражение в скобках: ${1} - {1}$. .....',
        answer='',
    )


def reduce_frac_mixed(s: ArithmState):
    if s.nnp != 0:
        gcd = math.gcd(s.nnp, s.nq)
        if gcd != 1:
            prev_np = s.nnp
            perv_q = s.nq
            s.nnp //= gcd
            s.nq //= gcd
            answer = f'${s.nwp} \\frac{{{s.nnp}}}{{{s.nq}}}$'
            s.add_step(
                action='Дробная часть — сократимая дробь. Запишем ответ, упростив дробную часть.',
                solution=(
                    f'Числитель и знаменатель дроби $\\frac{{{prev_np}}}{{{perv_q}}}$ делятся на ${gcd}$. '
                    f'Поделим числитель и знаменатель на ${gcd}$. '
                    f'Получится $\\frac{{{s.nnp}}}{{{s.nq}}}$. '
                    f'Запишем целую часть ${s.nwp}$ с упрощённой дробью $\\frac{{{s.nnp}}}{{{s.nq}}}$. '
                    f'Получается {answer}.'
                ),
                answer=answer,
            )


def reduce_frac_solo(s: ArithmState):
    gcd = math.gcd(s.sum_p, s.r1.q)
    if gcd != 1:
        np = s.sum_p // gcd
        nq = s.r1.q // gcd
        answer = f'$\\frac{{{np}}}{{{nq}}}$'
        s.add_step(
            action=f'Получившаяся дробь $\\frac{{{s.sum_p}}}{{{s.r1.q}}}$ — сократимая. Упростим дробь.',
            solution=(
                f'Числитель и знаменатель дроби $\\frac{{{s.sum_p}}}{{{s.r1.q}}}$ делятся на ${gcd}$. '
                f'Поделим числитель и знаменатель на ${gcd}$. Получится {answer}.'
            ),
            answer=answer,
        )


# add_wp
def remainder_and_frac_part_to_whole_add_whole(s: ArithmState):
    wps1 = '' if s.or1.wp == 0 else f'{s.or1.wp} '
    wps2 = '' if s.or2.wp == 0 else f'{s.or2.wp} '
    a1 = (f'{wps1}\\frac{{{s.or1.np}}}{{{s.or1.q}}}' if s.or1.np != 0 else wps1) or '0'
    a2 = (f'{wps2}\\frac{{{s.or2.np}}}{{{s.or2.q}}}' if s.or2.np != 0 else wps2) or '0'
    # if s.swapped:
    #     a1, a2 = a2, a1
    s.add_step(
        action=(
            f'Мы складывали ${a1}$ и ${a2}$, получили ${s.sum_wp} \\frac{{{s.sum_p}}}{{{s.nq}}}$. '
            f'Мы привели дробь $\\frac{{{s.sum_p}}}{{{s.nq}}}$ к целому числу и получили ${s.add_wp}$. '
            f'Сложим полученные целые числа.'
        ),
        solution=f'Сложим ${s.sum_wp}$ и ${s.add_wp}$. Получается ${utils.lat(s.ans, s.ns)}$.',
        answer=f'${utils.lat(s.ans, s.ns)}$',
    )


def second_fraction_to_mixed_subtr(s: ArithmState):
    s.add_step(
        action=(
            f'В дробной части уменьшаемого ${1}$ числитель больше знаменателя. '
            f'Запишем дробную часть в виде смешанного числа и прибавим к целой части ${1}$.'
        ),
        solution=(
            f'Разделим ${1}$ на ${1}$ с остатком. Частное равно ${1}$. Это целая часть. '
            f'Остаток равен ${1}$. Это числитель дробной части. Получается ${1}$. Целая часть ${1}$ была ${1}$. '
            f'Чтобы записать вычитаемое как смешанное число, прибавим к целой части ${1}$ преобразованное число ${1}$. '
            f'Получится ${1}$.'
        ),
        answer='',
    )


def second_greater_first(s: ArithmState):
    s.add_step(
        action=(
            'Второе число в выражении больше, чем первое. '
            'Вынесем минус за скобки, чтобы вычитать из большего меньшее.'
        ),
        solution=f'Напишем минус вне скобок, а внутри скобок поменяем числа местами. Получится: $-({1} - {1})$.',
        answer='',
    )


def second_mixed_frac_to_mixed(s: ArithmState):
    s.add_step(
        action=(
            f'В дробной части вычитаемого ${1}$ числитель больше знаменателя. '
            f'Запишем дробную часть в виде смешанного числа и прибавим к целой части ${1}$. '
            f'Перепишем всё вычитание с преобразованным вычитаемым.'
        ),
        solution=(
            f'Разделим ${1}$ на ${1}$ с остатком. '
            f'Частное равно ${1}$. Это целая часть. Остаток равен ${1}$. Это числитель дробной части. '
            f'Получается ${1}$. '
            f'Целая часть ${1}$ была ${1}$. '
            f'Чтобы записать вычитаемое как смешанное число прибавим к целой части ${1}$ преобразованное число ${1}$. '
            f'Получится ${1}$. '
            f'Перепишем вычитание, получится ${1} - {1}$.'
        ),
        answer='',
    )


def subtract_fractions(s: ArithmState):
    s.add_step(
        action='Вычтем дроби с одинаковым знаменателем.',
        solution=(
            f'Чтобы вычесть дроби с одинаковым знаменателем, из первого числителя ${1}$ вычтем второй числитель ${1}$, '
            f'а знаменатель перепишем без изменений. Получается ${1}$.'
        ),
        answer='',
    )


def subtraction(s: ArithmState):
    s.add_step(action=f'Вычтем ${1}$ и ${1}$.', solution=f'Из ${1}$ вычтем ${1}$. Получается ${1}$.', answer='')


def subtraction_with_minus(s: ArithmState):
    s.add_step(
        action=(
            f'Теперь ненадолго забудем про минус и будем работать только с выражением в скобках. '
            f'Из ${1}$ вычтем ${1}$.'
        ),
        solution=f'Из ${1}$ вычтем ${1}$. Получается ${1}$.',
        answer='',
    )


def two_negative(s: ArithmState):
    s.inverted = True
    s.r1.sgn = 1
    s.r2.sgn = 1
    s.f1 = -s.f1
    s.f2 = -s.f2
    s.ans = -s.ans
    s.add_step(
        action='Вынесем минус за скобки. ',
        solution=(
            f'Оба числа — отрицательные. '
            f'Значит, можно вынести минус за скобки, а внутри скобок записать сумму положительных чисел. '
            f'Получится: $-({s.r1} + {s.r2})$. '
            f'Теперь ненадолго забудем про минус и будем работать только с выражением в скобках. '
        ),
        answer='',
    )


def whole_minus_frac(s: ArithmState):
    s.add_step(
        action=f'После вычитания целых мы получили ${1}$. Осталось вычесть ${1}$.',
        solution=(
            f'Чтобы из ${1}$ вычесть ${1}$, запишем ${1}$ как сумму ${1}$ и ${1}$. '
            f'Сначала вычтем дробь из единицы. Для этого представим единицу как дробь со знаменателем ${1}$. '
            f'Это ${1}$. Из ${1}$ вычтем ${1}$, получится ${1}$. '
            f'Соберём что осталось: мы не трогали ${1}$, а в результате вычитания получилось ${1}$. '
            f'Итог запишем как смешанное число: ${1}$.'
        ),
        answer='',
    )


def wholes_difference(s: ArithmState):
    s.add_step(
        action=(
            f'Чтобы вычесть из целого смешанное число, сначала вычтем целую часть, а затем — дробную часть. '
            f'Сделаем первый шаг. Вычти из целого ${1}$ целую часть смешанного числа ${1}$.'
        ),
        solution=f'Целое число — ${1}$. Целая часть смешанного числа — ${1}$. Из ${1}$ вычтем ${1}$. Получается ${1}$.',
        answer='',
    )


def zero_difference(s: ArithmState):
    s.add_step(
        action=(
            'Теперь ненадолго забудем про минус и будем работать только с выражением в скобках. '
            'Вычтем из целой части смешанного числа целое. Дробную часть перепишем без изменений.'
        ),
        solution=(
            f'Целая часть смешанного числа — ${1}$. Целое — ${1}$. Их разность — ${1}$. '
            f'Мы не пишем ${1}$ как целое. Остается дробь ${1}$.'
        ),
        answer='',
    )


if __name__ == '__main__':
    eqs = [
        # целые
        '2 + 4',
        '2 - 4',
        '4 - 2',
        '4 - 4',
        '-2 + 4',
        '-4 + 2',
        '-4 + 4',
        '-2 - 4',
        # Целое + смешанная дробь
        '2 + 3 1/4',
        '2 + 3 2/4',
        '2 + 3 9/4',
        '2 + 3 8/4',
        '2 + 3 10/4',
        '3 1/4 + 2',
        '3 2/4 + 2',
        '3 9/4 + 2',
        '3 8/4 + 2',
        '3 10/4 + 2',
        # Целое + обыкновенная дробь
        '2 + 1/4',
        '2 + 2/4',
        '3 + 9/4',
        '3 + 8/4',
        '3 + 10/4',
        '1/4 + 2',
        '2/4 + 2',
        '9/4 + 3',
        '8/4 + 3',
        '10/4 + 3',
        # ОД + ОД, одинаковый знаменатель
        '10/9 + 5/9',
        '4/9 + 7/9',
        '4/9 + 2/9',
        '1/9 + 3/9',
        '1/9 + 17/9',
        '5/9 + 10/9',
        '7/9 + 4/9',
        '2/9 + 4/9',
        '3/9 + 1/9',
        '17/9 + 1/9',
        # ОД + ОД, разный знам
        '1/2 + 1/3',
        '2/5 + 1/10',
        '1/2 + 2/3',
        '1/2 + 5/6',
        '1/2 + 9/6',
        '1/3 + 1/2',
        '1/10 + 2/5',
        '2/3 + 1/2',
        '5/6 + 1/2',
        '9/6 + 1/2',
        # СД + СД, одинаковый знам
        '2 2/4 + 3 1/4',
        '2 3/4 + 3 1/4',
        '2 10/4 + 3 1/4',
        '2 1/6 + 3 2/6',
        '2 9/4 + 3 1/4',
        '3 1/4 + 2 2/4',
        '3 1/4 + 2 3/4',
        '3 1/4 + 2 10/4',
        '3 2/6 + 2 1/6',
        '3 1/4 + 2 9/4',
        # СД + СД, разный знам
        '2 1/2 + 3 1/3',
        '2 2/5 + 3 1/10',
        '2 1/2 + 3 2/3',
        '2 1/2 + 3 5/6',
        '2 1/2 + 3 9/6',
        '3 1/3 + 2 1/2',
        '3 1/10 + 2 2/5',
        '3 2/3 + 2 1/2',
        '3 5/6 + 2 1/2',
        '3 9/6 + 2 1/2',
        # СД + ОД, одинаковый знаменатель
        '2 2/4 + 1/4',
        '2 3/4 + 1/4',
        '2 10/4 + 1/4',
        '2 1/6 + 2/6',
        '2 9/4 + 1/4',
        '1/4 + 2 2/4',
        '1/4 + 2 3/4',
        '1/4 + 2 10/4',
        '2/6 + 2 1/6',
        '1/4 + 2 9/4',
        # СД + ОД, разный знаменатель
        '2 1/2 + 1/3',
        '2 2/5 + 1/10',
        '2 1/2 + 2/3',
        '2 1/2 + 5/6',
        '2 1/2 + 9/6',
        '1/3 + 2 1/2',
        '1/10 + 2 2/5',
        '2/3 + 2 1/2',
        '5/6 + 2 1/2',
        '9/6 + 2 1/2',
        # Оба отрицательные
        '- 2 1/2 + (- 3 1/3)',
        ' 2 1/2 + (- 3 1/3)',
        # яблоки
        '2 + 2',
        '9 + 1',
        '1 + 5',
        '7 + 11',

    ]
    for eq in eqs:
        steps = []
        sol = arithmetics(utils.parse(eq), steps, utils.NUM_STYLE.MIXED).ans
        print()
        print('Вычислите:')
        print(eq)
        utils.pprint(steps)
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    # import tests.test_simplification
    #
    # print(r'Running tests from tests/test_simplification.py')
    # tests.test_simplification.unittest.main(module=tests.test_simplification, exit=False)
