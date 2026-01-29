import sympy

from mathsolvers.solvers import simplification
from mathsolvers.solvers_stuff import classes, units_quantities
from mathsolvers.sympy_stuff import utils

__all__ = ['compare']

subs_vals = {q: u for (q, (u, v)) in units_quantities.UNITS_CONVERTER.items()}


def compare(exprs: list[str | sympy.Expr], reverse=False, ns: utils.NUM_STYLE = None) -> dict:
    result = {
        'task': ' \\ '.join(map(str, exprs)),
        'sol_codes': [],
    }
    if len(exprs) < 2:
        result['error'] = 'Сравнивать можно хотя бы два выражения'
        return result

    parseds = exprs.copy()
    if ns is None:
        ns = utils.NUM_STYLE.FRAC
    for ind, expr in enumerate(parseds):
        if not isinstance(expr, sympy.Expr):
            try:
                parsed = utils.parse(expr)
            except Exception:
                result['error'] = f'Выражение «{expr}» чёт не парсится'
                return result
            parseds[ind] = parsed
    steps: list[classes.Step] = []
    # Сначала упрощаем каждое выражение
    parseds_s = [utils.lat(expr, ns) for expr in parseds]

    simplefieds = parseds.copy()
    for ind, parsed in enumerate(simplefieds):
        simplefieds[ind] = simplification.with_vars(parsed, steps, ns)

    arg_sort = list(range(len(simplefieds)))

    has_units_inside = False
    try:
        arg_sort.sort(key=lambda ind: simplefieds[ind], reverse=reverse and len(simplefieds) > 2)
    except Exception:
        simplefieds_units = [expr.xreplace(subs_vals) for expr in simplefieds]
        try:
            arg_sort.sort(key=lambda ind: simplefieds_units[ind], reverse=reverse)
            has_units_inside = True
        except Exception:
            result['error'] = 'Не удалось упорядочить ' + ', '.join(parseds_s)
            return result

    # Если они все целые, то сразу ответ
    all_integers = all(el.is_Integer or isinstance(el, utils.DRational) for el in simplefieds)
    all_rationals = all(el.is_Rational for el in simplefieds)
    if all_rationals and not all_integers:
        denominators = [sympy.fraction(term)[1] for term in simplefieds]
        lcm_denom = sympy.lcm(denominators)
        all_denomed = []
        any_need = False
        for term in simplefieds:
            numer, denumer = sympy.fraction(term)
            need = lcm_denom // denumer
            if need > 1:
                any_need = True
            all_denomed.append(utils.FRational(numer * need, denumer * need, gcd=1))
        if any_need:
            simplefieds_s = '$, $'.join(utils.lat(expr, ns) for expr in simplefieds)
            all_denomed_s = '$, $'.join(utils.lat(expr, ns) for expr in all_denomed)
            steps.append(
                classes.Step(
                    action=(
                        f'Приведём все дроби ${simplefieds_s}$ к общему знаменателю '
                        f'и запишем в виде обыкновенной дроби.'
                    ),
                    solution=(
                        f'Приведём все дроби ${simplefieds_s}$ к общему знаменателю ${utils.lat(lcm_denom, ns)}$ '
                        f'и запишем в виде обыкновенной дроби. '
                        f'Получится ${all_denomed_s}$.'
                    ),
                    answer=f'${all_denomed_s}$',
                )
            )
    else:
        all_denomed = simplefieds

    all_denomed_s = [utils.lat(expr, ns) for expr in all_denomed]
    if len(all_denomed) == 2:
        dif = all_denomed[0] - all_denomed[1]
        if has_units_inside:
            dif = dif.xreplace(subs_vals)
        dif = dif.doit()
        if dif == 0:
            sgn = '='
            word = 'равно'
        elif arg_sort == [0, 1]:
            sgn = '<'
            word = 'меньше'
        else:
            sgn = '>'
            word = 'больше'
        any_changes = parseds_s != all_denomed_s
        verdict = f' Значит ${parseds_s[0]}$ {word} ${parseds_s[1]}$.' if any_changes else ''
        steps.append(
            classes.Step(
                action=f'Сравним ${all_denomed_s[0]}$ и ${all_denomed_s[1]}$.',
                solution=(f'${all_denomed_s[0]}$ {word} ${all_denomed_s[1]}$.' f'{verdict}'),
                answer=f'${parseds_s[0]} {sgn} {parseds_s[1]}$.',
            )
        )
    else:
        if reverse:
            sort_order = 'по убыванию'
        else:
            sort_order = 'по возрастанию'
        all_denomed_joined = '$; $'.join(all_denomed_s[ind] for ind in arg_sort)
        all_denomed_sorted_joined = f'{all_denomed_s[arg_sort[0]]}'
        all_parsed_sorted_joined = f'{parseds_s[arg_sort[0]]}'
        for ind in range(1, len(all_denomed_s)):
            eq = (all_denomed[arg_sort[ind]] - all_denomed[arg_sort[ind - 1]]).doit() == 0
            if eq:
                sgn = ' = '
            elif reverse:
                sgn = ' > '
            else:
                sgn = ' < '
            all_denomed_sorted_joined += sgn + all_denomed_s[arg_sort[ind]]
            all_parsed_sorted_joined += sgn + parseds_s[arg_sort[ind]]
        any_changes = all_denomed_sorted_joined != all_parsed_sorted_joined
        verdict = f' Значит ${all_parsed_sorted_joined}$.' if any_changes else ''
        steps.append(
            classes.Step(
                action=f'Упорядочим ${all_denomed_joined}$ {sort_order}.',
                solution=(
                    f'Упорядочим ${all_denomed_joined}$ {sort_order}. '
                    f'Получаем ${all_denomed_sorted_joined}$.'
                    f'{verdict}'
                ),
                answer=f'${all_parsed_sorted_joined}$.',
            )
        )

    result['final_answer'] = steps[-1]['answer']

    for i, step in enumerate(steps, start=1):
        result[f'step {i}'] = step
    return result


if __name__ == '__main__':
    # print(compare([utils.parse('3/7'), utils.parse('2/5')]))
    # print(compare([utils.parse('-64'), utils.parse('-2^6')]))
    print(compare([utils.parse('6ц'), utils.parse('623кг')]))
