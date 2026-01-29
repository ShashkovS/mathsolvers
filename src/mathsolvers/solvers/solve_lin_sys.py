import sympy

from mathsolvers.solvers_stuff import classes
from mathsolvers.sympy_stuff import utils

__all__ = ['solve_lin_sys']


def solve_lin_sys(*exprs: str, vars: list[str] | None = None) -> dict:
    one_line_system = r' \\ '.join(exprs)
    result = {
        'task': one_line_system,
        'sol_codes': [],
    }

    steps = []
    parsed = [utils.parse(expr) for expr in exprs]
    symbols = set()
    for eq in parsed:
        symbols |= eq.free_symbols
    result['sol_codes'].append(f'solve-sys-{len(parsed)}-eq')
    symbols = sorted(symbols, key=lambda n: n.name)
    result['sol_codes'].append(f'solve-sys-{len(symbols)}-vars')
    try:
        sols = sympy.solve(parsed, *symbols, dict=True)
    except Exception as e:
        if str(e) == 'can only solve for one symbol at a time':
            result['error'] = f'Пока не умеем решать системы неравенств {len(symbols)} переменных'
            return result
        raise
    if isinstance(sols, list):
        result['final_answer'] = (
            '$'
            + ' ; '.join(', '.join(f'{utils.lat(v)} = {utils.lat(r)}' for v, r in sol.items()) for sol in sols)
            + '$'
        )
        result['sol'] = [{v.name: f'{utils.lat(r)}' for v, r in sol.items()} for sol in sols]
        result['sol_codes'].append('solve-sys-eqs')
    else:
        result['sol'] = result['final_answer'] = f'${utils.lat(sols)}$'
        result['sol_codes'].append('solve-sys-ineqs-one-var')
    sys_s = f'$$\\begin{{cases}}{one_line_system}\\end{{cases}}$$'
    steps.append(
        classes.Step(
            action=f'Решим систему {sys_s}',
            solution=(f'Решим систему {sys_s}\n' f'Получим ответ {result["final_answer"]}'),
            answer=f'{result["final_answer"]}',
        )
    )

    for i, step in enumerate(steps, start=1):
        result[f'step {i}'] = step
    return result


if __name__ == '__main__':
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    import tests.test_solve_lin_sys

    print(r'Running tests from tests/test_solve_lin_sys.py')
    tests.test_solve_lin_sys.unittest.main(module=tests.test_solve_lin_sys, exit=False)
