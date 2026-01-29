import re
import sys

from mathsolvers import solvers

__all__ = ['solver', 'solve']

_RE_PARSE = re.compile(r'(?:<<|«|\[\[)\s*(\w+)\s*(.*?)\s*\.?\s*(?:>>|»|\]\])', flags=re.DOTALL)
_RE_SPLIT = re.compile(r'\s*\\\\\s*')
_RE_SPLIT_COMPARE = re.compile(r'\s*(?:\\\\|<=|>=|<|>|=)\s*')
_RE_FINAL = re.compile(r'\b[fF]inal_answer:?\s+([\s\S]*?)(?=\s*\n\s*\n|$|(?:"?(?:\d+\s*)[aA]ction))')
_RE_INEQS = re.compile(r'(>=|<=|<|>)')

RECURSION_LIMIT_TO_PREVENT_LONG_COMPUTATION = 250
sys.setrecursionlimit(RECURSION_LIMIT_TO_PREVENT_LONG_COMPUTATION)


def solver(expr: str | list[str]) -> dict:
    """Распарсить вызов решателя вида `<<func parms>>`, выполнить и вернуть результат
    Args:
        expr: строка вида <<func parms>>

    Returns:
    Словарь с решением алгорешателя

    """
    if isinstance(expr, (list, tuple)):
        expr = '\n'.join(expr)
    # now expr is string
    matches = list(_RE_PARSE.finditer(expr))
    if not matches:
        return {'task': expr, 'error': 'Не найден шаблон <<func ...>>'}
    all_callers_res = []
    for match in matches:
        func, parms = match.groups()
        parms = parms.strip(' \t=.')
        try:
            res = _call_give_solver(expr, func, parms)
        except Exception as e:
            res = {'task': match.group(0), 'error': f'Ошибка алгорешателя {func}: {e}'}
        all_callers_res.append(res)
    if len(all_callers_res) == 1:
        # Если вызов один, то возвращаем его.
        return all_callers_res[0]
    else:
        # Вызовов больше одного, нужно объединить результаты
        # Всё завершилось ошибкой
        if all(res.get('error') for res in all_callers_res):
            return {
                'task': expr,
                'error': '\n'.join(res['error'] for res in all_callers_res)
            }
        # есть хоть один успешный
        cur_step = 0
        final_answers = []
        error = ''
        total_res = {
            'task': expr,
        }
        for res in all_callers_res:
            if res.get('error'):
                error += res['error'] + '\n'
            else:
                for key, val in res.items():
                    if key == 'final_answer':
                        final_answers.append(res['final_answer'])
                    elif key.startswith('step '):
                        cur_step += 1
                        total_res[f'step {cur_step}'] = val
        if error:
            total_res['error'] = error
        total_res['final_answer'] = '; '.join(final_answers)
        return total_res


def solve(expr: str, *other_exprs: str, vars: str | list[str] | None = None) -> dict:
    """Solve — Решить уравнение, систему, неравенство
    Args:
        expr: уравнение/неравенство
        *other_exprs: ещё уравнения, при решении системы
        vars:

    Returns:
    Словарь с решением

    """
    if isinstance(vars, str):
        vars = [vars]
    elif vars is None:
        vars = []

    if not other_exprs:
        solution = solvers.solve_single_var(expr, vars=vars)
        return solution.as_dict()
    solution = solvers.solve_lin_sys(expr, *other_exprs, vars=vars)
    return solution


def _call_give_solver(expr: str, func: str, parms: str) -> dict:
    if func == 'solve':
        args = _RE_SPLIT.split(parms)
        # Возможно, это неявная система неравенств типа <<solve 2 > x > 3>>, тогда мы переделаем её в систему
        if len(args) == 1:
            ineq_parts = _RE_INEQS.split(parms)
            if len(ineq_parts) > 3:
                args = [''.join(ineq_parts[i: i + 3]) for i in range(0, len(ineq_parts) - 1, 2)]
        if len(args) == 1:
            return solve(*args)
        return solvers.solve_lin_sys(*args)
    if func == 'calc':
        return {'task': expr, 'answer': solvers.calc(parms)}
    if func == 'simplify':
        expr, *args = _RE_SPLIT.split(parms)
        subs = {}
        for arg in args:
            x, val = arg.split('=')
            subs[x.strip()] = val.strip()
        if not subs:
            return solvers.simplify(expr)
        return solvers.subs(expr, subs)
    if func == 'factor':
        return solvers.factor(parms)
    if func == 'units':
        expr, *args = _RE_SPLIT.split(parms)
        return solvers.units(expr, args)
    if func == 'format':
        expr, *args = _RE_SPLIT.split(parms)
        if len(args) != 1:
            return {'task': expr, 'error': 'Необходимо указать, в какой формат преобразовать'}
        return solvers.format(expr, args[0])
    if func == 'compare':
        exprs = _RE_SPLIT_COMPARE.split(parms)
        reverse = False
        while 'reverse' in exprs:
            exprs.pop(exprs.index('reverse'))
            reverse = True
        return solvers.compare(exprs, reverse)
    return {'task': expr, 'error': f'Неизвестная функция {func}'}
