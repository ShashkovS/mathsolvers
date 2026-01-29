import sympy

from mathsolvers import sympy_stuff
from mathsolvers.solvers_stuff import classes
from mathsolvers.sympy_stuff import utils

__all__ = ['factor']


def factor(expr: str) -> dict:
    """Factor — разложить число или выражение на множители
    Args:
        expr: выражение

    Returns:
    Словарь с решением

    """
    result = {
        'task': expr,
        'sol_codes': [],
    }

    steps = []
    parsed, ns = sympy_stuff.utils.parse_and_ns(expr)
    before_s = sympy_stuff.utils.lat(parsed, ns)
    if parsed.free_symbols:
        after = sympy.factor(parsed)
        if after.is_Mul:
            after = sympy.Mul(*(sympy_stuff.utils.normalize_terms_order(term) for term in after.args), evaluate=False)
        elif after.is_Pow:
            after = sympy.Pow(sympy_stuff.utils.normalize_terms_order(after.args[0]), after.args[1], evaluate=False)
        after_s = sympy_stuff.utils.lat(after, ns)
        steps.append(
            classes.Step(
                action=f'Разложим выражение ${before_s}$ на множители.',
                solution=(f'Разложим выражение ${before_s}$ на множители. ' f'Получим ${before_s} = {after_s}$'),
                answer=f'${after_s}$',
            )
        )
        result['sol_codes'].append('factor-expr')
    else:
        after = parsed
        if parsed.is_Integer:
            factors = sympy.factorint(parsed, multiple=True)
            after = sympy.Mul(*factors, evaluate=False)
            result['sol_codes'].append('factor-int')
        elif parsed.is_Add and parsed.is_positive and parsed.has(sympy.Pow) and parsed.is_constant():
            squared = sympy.sqrt(parsed)
            denested = sympy.sqrtdenest(squared, max_iter=3)
            if utils.has_significant_change(squared, denested, ns):
                after = sympy.Pow(denested, 2, evaluate=False)
                result['sol_codes'].append('factor-denest')
        after_s = sympy_stuff.utils.lat(after, ns)
        steps.append(
            classes.Step(
                action=f'Разложим число ${before_s}$ на множители.',
                solution=(f'Разложим число ${before_s}$ на множители. ' f'Получим ${before_s} = {after_s}$'),
                answer=f'${after_s}$',
            )
        )
        result['sol_codes'].append('factor-expr')
    result['final_answer'] = f'${sympy_stuff.utils.lat(parsed, ns)} = {sympy_stuff.utils.lat(after, ns)}$'

    for i, step in enumerate(steps, start=1):
        result[f'step {i}'] = step
    return result


if __name__ == '__main__':
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    import tests.test_factor_expr

    print(r'Running tests from tests/test_factor_expr.py')
    tests.test_factor_expr.unittest.main(module=tests.test_factor_expr, exit=False)
