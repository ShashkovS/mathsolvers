import sympy

from mathsolvers.sympy_stuff import utils

__all__ = ['solve_eq']


def solve_eq(expr: str) -> dict:
    result = {
        'task': expr,
    }
    if expr.count('=') != 1:
        result['error'] = f'В выражении «{expr}» должен быть ровно один символ равенства «=»'
        return result
    try:
        parsed = utils.parse(expr)
    except Exception:
        result['error'] = f'Выражение «{expr}» чёт не парсится'
        return result
    vars = sorted(parsed.free_symbols, key=lambda var: var.name)
    if len(vars) == 0:
        result['error'] = f'В выражении «{expr}» нет переменных'
        return result
    if len(vars) > 1:
        result['error'] = f'В выражении «{expr}» больше одной переменной: {", ".join(map(str, vars))}'
        return result
    x = vars.pop()
    sol = sympy.solveset(parsed, x, domain=sympy.S.Reals)
    ns = utils.get_num_style(expr)
    if sol != sympy.Reals:
        result['answers'] = [utils.lat(ans, ns) for ans in sol]
    else:
        result['answers'] = ['(-\\infty, +\\infty)']
    return result
