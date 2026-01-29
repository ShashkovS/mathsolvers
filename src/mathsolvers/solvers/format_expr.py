import enum

import sympy

from mathsolvers.solvers import simplification
from mathsolvers.solvers_stuff import classes
from mathsolvers.sympy_stuff import utils

__all__ = ['format', 'FORMAT']


class FORMAT(enum.StrEnum):
    FRAC = 'frac'
    MIX = 'mix'
    DEC = 'dec'
    PERC = 'perc'


dest_num_fmt = {
    FORMAT.FRAC: utils.NUM_STYLE.FRAC,
    FORMAT.MIX: utils.NUM_STYLE.MIXED,
    FORMAT.DEC: utils.NUM_STYLE.DECIMAL,
    FORMAT.PERC: utils.NUM_STYLE.DECIMAL,
}

dest_num_fmt_text = {
    FORMAT.FRAC: 'в обыкновенную дробь',
    FORMAT.MIX: 'в смешанную дробь',
    FORMAT.DEC: 'в десятичную дробь',
    FORMAT.PERC: 'в проценты',
}


def to_mixed(expr: sympy.core.Rational) -> utils.MRational:
    p, q = expr.p, expr.q
    sgn = -1 if p < 0 else 1
    p = abs(p)
    wp, np = divmod(p, q)
    if sgn == -1:
        if wp != 0:
            wp = -wp
        else:
            np = -np
    return utils.MRational(wp, np, q)


def _is_repeating_fraction(q):
    while q % 2 == 0:
        q //= 2
    while q % 5 == 0:
        q //= 5
    return q != 1


def _change_fmt(
    expr: sympy.Expr,
    fmt: FORMAT,
    src_ns: utils.NUM_STYLE,
    dst_ns: utils.NUM_STYLE,
    steps: list[classes.Step],
    sol_codes: list[str],
) -> sympy.Expr:
    if expr.is_Rational:
        expr_type = type(expr)
        if expr_type == utils.DRational:
            sol_codes.append('format-from-dec')
            if fmt == FORMAT.FRAC:
                res = utils.FRational(expr.p, expr.q)
            elif fmt == FORMAT.MIX:
                res = to_mixed(expr)
            elif fmt == FORMAT.DEC:
                if _is_repeating_fraction(expr.q):
                    res = utils.PRational(expr.p, expr.q)
                    sol_codes.append('format-to-periodic')
                else:
                    res = utils.DRational(expr.p, expr.q)
            elif fmt == FORMAT.PERC:
                res = sympy.Mul(utils.DRational(expr.p * 100, expr.q), utils.pcnt)
        elif expr_type == utils.MRational:
            sol_codes.append('format-from-mix')
            if fmt == FORMAT.FRAC:
                res = utils.FRational(expr.p, expr.q)
            elif fmt == FORMAT.MIX:
                res = expr
            elif fmt == FORMAT.DEC:
                if _is_repeating_fraction(expr.q):
                    res = utils.PRational(expr.p, expr.q)
                    sol_codes.append('format-to-periodic')
                else:
                    res = utils.DRational(expr.p, expr.q)
            elif fmt == FORMAT.PERC:
                res = sympy.Mul(utils.DRational(expr.p * 100, expr.q), utils.pcnt)
        elif expr_type == utils.PRational:
            sol_codes.append('format-from-periodic')
            if fmt == FORMAT.FRAC:
                res = utils.FRational(expr.p, expr.q)
            elif fmt == FORMAT.MIX:
                res = to_mixed(expr)
            elif fmt == FORMAT.DEC:
                res = expr
            elif fmt == FORMAT.PERC:
                res = sympy.Mul(utils.PRational(expr.p * 100, expr.q), utils.pcnt)
        else:
            sol_codes.append('format-from-frac')
            # обычный Rational или FRational
            if fmt == FORMAT.FRAC:
                res = expr
            elif fmt == FORMAT.MIX:
                res = to_mixed(expr)
            elif fmt == FORMAT.DEC:
                if _is_repeating_fraction(expr.q):
                    res = utils.PRational(expr.p, expr.q)
                    sol_codes.append('format-to-periodic')
                else:
                    res = utils.DRational(expr.p, expr.q)
            elif fmt == FORMAT.PERC:
                res = sympy.Mul(utils.DRational(expr.p * 100, expr.q), utils.pcnt)
        expr_s = utils.lat(expr)
        res_s = utils.lat(res)
        if expr_s != res_s:
            steps.append(
                classes.Step(
                    action=f'Преобразуем число ${expr_s}$ в {dest_num_fmt_text[fmt]}.',
                    solution=f'Преобразуем число ${expr_s}$. Получится ${res_s}$',
                    answer=f'${res_s}$',
                )
            )
        return res
    if (
        fmt != FORMAT.PERC and expr.is_Mul and any(arg.is_Symbol and arg.name == 'pcnt' for arg in expr.args)
    ):  # проценты
        sol_codes.append('format-from-perc')
        expr_s = utils.lat(expr, dst_ns)
        new_args = list(expr.args)
        for i, el in enumerate(new_args):
            if el.is_Symbol and el.name == 'pcnt':
                new_args[i] = utils.DRational(1, 100)
        new_expr = sympy.Mul(*new_args, evaluate=False)
        new_expr_s = utils.lat(new_expr, dst_ns)
        steps.append(
            classes.Step(
                action=f'Процент — это $0,01$, одна сотая часть. Заменим в ${expr_s}$ процент на сотую.',
                solution=(
                    f'Процент — это $0,01$, одна сотая часть. '
                    f'Заменим в ${expr_s}$ процент на сотую. '
                    f'Получится ${new_expr_s}$'
                ),
                answer=f'${new_expr_s}$',
            )
        )
        return new_expr
    if expr.args:
        new_args = [_change_fmt(arg, fmt, src_ns, dst_ns, steps, sol_codes) for arg in expr.args]
        return expr.func(*new_args, evaluate=False)
    return expr


def format(expr: str | sympy.Expr, fmt: str | FORMAT, ns: utils.NUM_STYLE = None) -> dict:
    r"""Format — Преобразования между записями чисел
    (неправильная дробь frac, смешанная mix, десятичная dec, периодическая dec, проценты perc)

    Args:
        expr: выражение (строка или sympy)

    Returns:
    Словарь с решением
    # >>> format(r'\\frac{1}{2}', 'dec')['final_answer']
    # '$0{,}5$'
    # >>> format(r'0,5', 'frac')['final_answer']
    # '$\\frac{1}{2}$'
    # >>> format(r'0,(3)', 'frac')['final_answer']
    # '$\\frac{1}{3}$'
    # >>> format(r'\\frac{10}{6}', 'mix')['final_answer']
    # '$1\\frac{2}{3}$'
    # >>> format(r'1 \\frac{4}{6}', 'frac')['final_answer']
    # '$\\frac{5}{3}$'
    # >>> format(r'0,5', 'perc')['final_answer']
    # '$50 \\%$'
    # >>> format(r'50\%', 'frac')['final_answer']
    # '$\\frac{1}{2}$'
    # >>> format(r'50\%', 'dec')['final_answer']
    # '$0{,}5$'
    # >>> format(r'\\frac{1}{3}', 'dec')['final_answer']
    # '$0,(3)$'

    """
    result = {
        'task': expr,
        'sol_codes': [],
    }

    if isinstance(expr, sympy.Expr):
        parsed = expr
        ns = ns or utils.get_num_style(utils.hum(expr))
    else:
        expr_pcnt = expr.replace('\\%', ' * pcnt ').replace('%', ' * pcnt ')
        try:
            parsed, ns = utils.parse_and_ns(expr_pcnt)
        except Exception:
            result['error'] = f'Выражение «{expr}» чёт не парсится'
            return result
    try:
        fmt = FORMAT(fmt)
    except ValueError:
        result['error'] = f'Формат {fmt} неверный, допустимы {", ".join(FORMAT)}'
        return result

    if '%' in expr:
        result['sol_codes'].append('format-from-perc')
    # Сначала упрощаем выражение
    steps: list[classes.Step] = []
    simplefied1 = simplification.with_vars(parsed, steps, ns)
    dst_ns = dest_num_fmt[fmt]
    changed = _change_fmt(simplefied1, fmt, ns, dst_ns, steps, result['sol_codes'])
    simplefied2 = simplification.with_vars(changed, steps, dst_ns)
    result['sol_codes'].append(f'format-to-{fmt}')

    ans_s = utils.lat(simplefied2, dst_ns)
    result['final_answer'] = f'${ans_s}$'
    if len(steps) == 0:
        parsed_s = utils.lat(parsed, ns)
        steps.append(
            classes.Step(
                action=f'Нужно ли что-то менять, чтобы преобразовать ${parsed_s}$ {dest_num_fmt_text[fmt]}?',
                solution=f'Все числа в ${parsed_s}$ итак в нужном формате, оставим всё без изменений.',
                answer=f'${ans_s}$',
            )
        )

    for i, step in enumerate(steps, start=1):
        result[f'step {i}'] = step
    return result
