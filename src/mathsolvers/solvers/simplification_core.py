import math
from dataclasses import dataclass

import sympy

from mathsolvers.solvers_stuff.classes import CHANGE
from mathsolvers.sympy_stuff import utils


@dataclass
class _State:
    expr: sympy.Expr
    change: CHANGE = CHANGE.NoChange
    before: sympy.Expr = None
    after: sympy.Expr = None
    expr_after: sympy.Expr = None
    dif: sympy.Expr = None

    def __str__(self):
        return (
            f'State({utils.lat(self.expr)} -> {utils.lat(self.expr_after)} '
            f'({self.change}) '
            f'{utils.lat(self.before)} -> {utils.lat(self.after)})'
        )


def _is_num(expr):
    return isinstance(expr, (int, float)) or expr.is_Rational


def _step_mul(expr: sympy.Expr, new_args: list[sympy.Expr], state: _State, done_set: set[sympy.Expr], ns) -> sympy.Expr:
    after_eval = expr.func(*new_args, evaluate=False)
    numer, denom = utils.split_numer_denom(after_eval)
    new_after = utils.mul_from_numer_denom(numer, denom)
    new_after = utils.normalize_terms_order(new_after)
    # возможно несущественное изменение: внесение -1 в один из рациональных множителей >>:-I
    if len(numer) + len(denom) > 0 and utils.has_significant_change_ignore_pm(expr, new_after, ns):
        state.expr_after = state.after = new_after
        state.before = expr
        if set(expr.args) - (set(new_after.args) if new_after.args else {new_after}) == {1}:
            state.change = CHANGE.RemoveOnes
        elif denom:
            state.change = CHANGE.CollectNumerAndDenumer
        else:
            state.change = CHANGE.CollectNumer
        return state.expr_after
    # Так, переупорядочивание не помогает. Пробуем сократить
    if denom:
        new_after = sympy.cancel(after_eval)
        numer_aft, denom_aft = utils.split_numer_denom(new_after)
        new_after = utils.mul_from_numer_denom(numer_aft, denom_aft)
        new_after = utils.normalize_terms_order(new_after)
        # print(f'{numer=} {numer_aft=} {numer != numer_aft=}')
        # print(f'{denom=} {denom_aft=} {denom != denom_aft=}')
        if len(numer) + len(denom) > len(numer_aft) + len(denom_aft) and utils.has_significant_change_ignore_pm(
                expr, new_after, ns
        ):
            state.expr_after = state.after = new_after
            state.before = expr
            state.change = CHANGE.CalcelMuls
            return state.expr_after
    new_after = after_eval.doit()
    if not new_after.is_Rational:
        numer_aft, denom_aft = utils.split_numer_denom(new_after)
        new_after = utils.mul_from_numer_denom(numer_aft, denom_aft)
        new_after = utils.normalize_terms_order(new_after)
    # Нужно выкинуть особый случай: в выражении было ровно одно десятичное число.
    # Тогда оно не могло измениться, хотя конструкция выше его «размажет»
    if len(new_after.args) <= len(expr.args) and utils.has_significant_change(expr, new_after, ns):
        state.expr_after = state.after = new_after
        state.before = expr
        state.change = CHANGE.DoitMul
        return state.expr_after
    if after_eval.has(sympy.Add):
        after_eval = sympy.expand(after_eval, deep=False)
        numer_aft, denom_aft = utils.split_numer_denom(after_eval)
        after_eval = utils.mul_from_numer_denom(numer_aft, denom_aft)
        after_eval = utils.normalize_terms_order(after_eval)
        if utils.has_significant_change(expr, after_eval, ns):
            state.expr_after = state.after = after_eval
            state.before = expr
            state.change = CHANGE.ExpandMul
            done_set.add(state.after)
            return state.expr_after
    # Так, переупорядочивание не помогает. Пробуем собрать степени
    new_after = sympy.powsimp(after_eval, deep=False)
    new_after = sympy.powdenest(new_after)
    numer_aft, denom_aft = utils.split_numer_denom(new_after)
    new_after = utils.mul_from_numer_denom(numer_aft, denom_aft)
    new_after = utils.normalize_terms_order(new_after)
    if (not new_after.is_Mul or len(new_after.args) < len(expr.args)) and utils.has_significant_change(
            expr, new_after, ns
    ):
        state.expr_after = state.after = utils.normalize_terms_order(new_after)
        state.before = expr
        # TODO Здесь powsimp делает слишком много с числами :(
        state.change = CHANGE.Unknown
        done_set.add(state.after)
        return state.expr_after
    state.expr_after = expr
    done_set.add(expr)
    return state.expr_after


def _step_pow(expr: sympy.Expr, new_args: list[sympy.Expr], state: _State, done_set: set[sympy.Expr], ns) -> sympy.Expr:
    after_eval = expr.func(*new_args, evaluate=False)
    if not new_args[0].free_symbols and new_args[0].has(sympy.Pow) and new_args[1] == sympy.core.S.Half:
        new_after = sympy.sqrtdenest(after_eval, max_iter=3)
        if utils.has_significant_change(expr, new_after, ns):
            state.expr_after = state.after = utils.normalize_terms_order(new_after)
            state.before = expr
            state.change = CHANGE.SqrtDenest
            done_set.add(state.after)
            return state.expr_after
    elif expr.args[1] != sympy.core.S.NegativeOne:
        if (
                (new_args[0].is_Rational and new_args[1].is_Rational)
                and (abs(new_args[1]) >= 5 and not 5e-5 <= abs(expr.doit()) <= 2e4)
        ):
            # Не разворачиваем большие степени
            state.expr_after = expr
            done_set.add(expr)
            return state.expr_after
        after_eval = after_eval.doit().expand()
        if utils.has_significant_change(expr, after_eval, ns):
            state.expr_after = state.after = utils.normalize_terms_order(after_eval)
            state.before = expr
            state.change = CHANGE.DoitPow
            done_set.add(state.after)
            return state.expr_after
    state.expr_after = expr
    done_set.add(expr)
    return state.expr_after


def _step_add(expr: sympy.Expr, new_args: list[sympy.Expr], state: _State, done_set: set[sympy.Expr], ns) -> sympy.Expr:
    after_eval = expr.func(*new_args, evaluate=False)
    after_eval = after_eval.doit()
    # after_eval = sympy.ratsimp(after_eval)  # TODO!
    # after_eval = sympy.expand(
    # deep=False, modulus=None, power_base=False, power_exp=False, mul=False, log=False, multinomial=False, basic=False
    # )
    after_eval = utils.normalize_terms_order(sympy.expand(after_eval, deep=False))
    if utils.has_significant_change(expr, after_eval, ns):
        state.expr_after = state.after = after_eval
        state.before = expr
        state.change = CHANGE.DoitAdd
        # Результат сложения может быть сократимой дробью, поэтому пока не добавляем в done_set
        if not state.after.is_Rational:
            done_set.add(state.after)
        return state.expr_after
    state.expr_after = expr
    done_set.add(expr)
    return state.expr_after


def _step_div(expr: sympy.Expr, new_args: list[sympy.Expr], state: _State, done_set: set[sympy.Expr], ns) -> sympy.Expr:
    if len(new_args) == 2 and new_args[0].is_Integer and new_args[1].is_Integer:
        after_eval = sympy.Rational(*new_args)
        state.expr_after = state.after = after_eval
        state.before = expr
        state.change = CHANGE.DivInts
        done_set.add(state.after)
        return state.expr_after
    after_eval = expr.func(*new_args, evaluate=False)
    after_eval = after_eval.doit()
    after_eval = utils.normalize_terms_order(sympy.expand(after_eval, deep=False))
    if utils.has_significant_change(expr, after_eval, ns):
        state.expr_after = state.after = after_eval
        state.before = expr
        state.change = CHANGE.Div
        done_set.add(state.after)
        return state.expr_after
    state.expr_after = expr
    done_set.add(expr)
    return state.expr_after


def _step_other(
        expr: sympy.Expr, new_args: list[sympy.Expr], state: _State, done_set: set[sympy.Expr], ns
) -> sympy.Expr:
    after_eval = expr.func(*new_args, evaluate=False)
    after_eval = sympy.expand(after_eval.doit(), deep=False)
    if utils.has_significant_change(expr, after_eval, ns):
        state.expr_after = state.after = utils.normalize_terms_order(after_eval)
        state.before = expr
        state.change = CHANGE.Unknown
        done_set.add(state.after)
        return state.expr_after
    state.expr_after = expr
    done_set.add(expr)
    return state.expr_after


def _make_one_step(expr: sympy.Expr, state: _State, done_set: set[sympy.Expr], ns) -> sympy.Expr:
    """Сделать один шаг в упрощении выражений.
    Рекурсивная функция, которая ищет, что бы упростить в дереве выражения

    # TODO Вообще это — очень хитрая и важная функция. Но сейчас в ней всё плохо :(
    """
    state.expr_after = expr
    # Где-то в поддереве уже сделано какое-то изменение. Больше ничего не делаем
    if state.change != CHANGE.NoChange or (expr.is_Atom and not expr.is_Rational) or expr in done_set:
        if state.expr_after.func.__name__ == 'Pr':
            state.expr_after = state.expr_after.args[0]
        return state.expr_after

    if expr.args:
        new_args = [_make_one_step(arg, state, done_set, ns) for arg in expr.args]
        # print(f'name={type(expr)} expr={utils.lat(expr)} new_args=[{", ".join(utils.lat(arg) for arg in expr.args)}]')
        # print(f'{expr=} {expr.args=} {new_args=}')
        # Рекурсия может испортить
        state.expr_after = expr
        # =======================
        # Так, возможно на этом уровне никакие преобразования не нужны
        # ещё раз проверяем, так как рекурсивный _make_one_step мог сделать какие-то шаги
        if state.change != CHANGE.NoChange:
            state.expr_after = expr.func(*new_args, evaluate=False)
            if state.expr_after.func.__name__ == 'Pr':
                state.expr_after = state.expr_after.args[0]
            return state.expr_after
        # Если это просто «сохраняемые скобки», то раскрываем их
        if expr.func.__name__ == 'Pr':  # (см. mathsolvers.sympy_stuff.patched_parenthesis)
            state.expr_after = new_args[0]
            done_set.add(state.expr_after)
            return state.expr_after
        # Не рассматриваем деление на дробь, сразу выполняем
        if expr.is_Pow and new_args[0].is_Rational and new_args[1] == -1:
            state.expr_after = expr.func(*new_args, evaluate=True)
            done_set.add(state.expr_after)
            return state.expr_after
        # # если степень большая, то не возводим TODO
        # elif (expr.is_Pow
        #       and (new_args[0].is_Rational and new_args[1].is_Rational)
        #       and (abs(new_args[1]) >= 5 and not 1e-5 <= abs(expr.doit()) <= 1e6)):
        #     state.expr_after = expr.func(*new_args, evaluate=False)
        #     done_set.add(state.expr_after)
        #     return state.expr_after

        # # Не рассматриваем умножение -1 на то, что уже посчитано, если это где-то внутри
        # elif (
        #         state.expr is not expr
        #         and expr.is_Mul and len(expr.args) == 2
        #         and expr.args[0] in {1, -1} and expr.args[1] in done_set
        # ):
        #     state.expr_after = expr.func(*new_args, evaluate=True)
        #     done_set.add(state.expr_after)
        #     return state.expr_after
        # =======================
        # Пытаемся сделать какое-нибудь упрощающее преобразование
        if expr.is_Mul:
            return _step_mul(expr, new_args, state, done_set, ns)
        if expr.is_Pow:
            return _step_pow(expr, new_args, state, done_set, ns)
        if expr.is_Add:
            return _step_add(expr, new_args, state, done_set, ns)
        if expr.func.__name__ == 'PDiv':  # см. mathsolvers.sympy_stuff.patched_div.PDiv
            return _step_div(expr, new_args, state, done_set, ns)
        return _step_other(expr, new_args, state, done_set, ns)
    if expr.is_Rational:
        gcd = math.gcd(abs(expr.p), expr.q)
        if gcd > 1:
            cancelled = sympy.core.Rational(expr.p // gcd, expr.q // gcd, gcd=1)
            state.before = expr
            state.expr_after = state.after = cancelled
            state.change = CHANGE.CancelRational
            done_set.add(state.after)
            return state.expr_after
    state.expr_after = expr
    done_set.add(expr)
    return state.expr_after
