import re
# from random import choice, seed

import sympy

from mathsolvers.solvers import school_arithmetics, simplification_core
from mathsolvers.solvers_stuff import classes
from mathsolvers.solvers_stuff.classes import CHANGE, Step
from mathsolvers.sympy_stuff import utils

__all__ = ['simplify', 'calc', 'subs']


# Штука для массового анализа решений
# _counted = {}
#
# def _tmp_calc_change(state: simplification_core._State, ns: utils.NUM_STYLE):
#     if state.change == CHANGE.NoChange:
#         return
#     conv = f'$${utils.lat(state.before, ns)} \\quad {utils.lat(state.after, ns)}$$'
#     cng = state.change
#     key = (cng, conv)
#     # print(key)
#     _counted[key] = _counted.get(key, 0) + 1


def step_by_step_and_res(
    expr: str | sympy.Expr, ns=utils.NUM_STYLE.FRAC, *, fin_simplify=False, fix_expand=False
) -> tuple[list[simplification_core._State], sympy.Expr]:
    if isinstance(expr, str):
        expr = utils.parse(expr)
    steps = []
    done_set = set()
    prev_ans_s = ''
    while True:
        state = simplification_core._State(expr)
        expr = simplification_core._make_one_step(expr, state, done_set, ns)
        if state.change == CHANGE.NoChange:
            break
        # _tmp_calc_change(state, ns)
        # print(f'{str(expr):<40} {str(state.before):<20} -> {str(state.after):<20}  {str(state.change)}')
        # Блин, это — какое-то чёртово шаманство, его нужно переделать... Но хз как
        next_ans_s = utils.lat(state.expr_after, ns)
        if next_ans_s != prev_ans_s and utils.lat(state.before, ns) != utils.lat(state.after, ns):
            steps.append(state)
            prev_ans_s = next_ans_s
    if steps:
        steps[-1].expr_after = expr
    expr_after = steps[-1].expr_after if steps else expr
    # expr_after = steps[-1].expr_after if steps else expr
    # Особый случай. Мы упрощаем равенство/неравенство, и по краям уже всё сделали.
    # TODO (Почему это здесь??)
    if expr_after.is_Relational and expr_after.rhs != 0 and not expr_after.lhs.is_Symbol:
        state = simplification_core._State(expr_after)
        new_expr = expr_after.__class__(
            sympy.Add(expr_after.lhs, -expr_after.rhs, evaluate=False),
            0,
            evaluate=False,
        )
        state.before = expr_after
        state.after = state.expr_after = new_expr
        state.change = CHANGE.SubFromBothPartOfRel
        steps.append(state)
        state.dif = expr_after.rhs
        while True:
            state = simplification_core._State(new_expr)
            new_expr = simplification_core._make_one_step(new_expr, state, done_set, ns)
            if state.change == CHANGE.NoChange:
                break
            # _tmp_calc_change(state, ns)
            steps.append(state)
    elif fin_simplify:
        simplified = expr_after.simplify()
        if fix_expand:
            simplified = simplified.expand()
        expr_after_simp = utils.normalize_terms_order(simplified)
        if utils.has_significant_change_ignore_pm(expr_after, expr_after_simp, ns):
            state = simplification_core._State(expr_after)
            state.before = expr_after
            expr = state.after = state.expr_after = expr_after_simp
            state.change = CHANGE.Unknown
            steps.append(state)
    res = steps[-1].expr_after if steps else expr
    return steps, res


def step_by_step_str(expr: str | sympy.Expr, ns=utils.NUM_STYLE.FRAC) -> str:
    """Упростить выражение, вернуть строку с промежуточными вычислениями
    Args:
        expr: выражение
        ns: предпочитаемый тип чисел (дроби, смешанные, десятичные)

    Returns:
    Строку

    """
    return step_by_step_str_and_res(expr, ns)[0]


def step_by_step_str_and_res(
    expr: str | sympy.Expr, ns=utils.NUM_STYLE.FRAC, *, fin_simplify=False, fix_expand=False
) -> tuple[str, sympy.Expr]:
    """Упростить выражение и вернуть строку с шагами упрощения, и итоговый результат как sympy.Expr"""
    if isinstance(expr, str):
        try:
            expr, ns = utils.parse_and_ns(expr)
        except Exception as e:
            return f"error: {e} {getattr(e, 'text', '')}", None
    steps, res = step_by_step_and_res(expr, ns, fin_simplify=fin_simplify, fix_expand=fix_expand)
    if not steps:
        return utils.lat(expr, ns), expr
    steps_strings = [utils.lat(expr, ns)]
    for simp_step in steps:
        step_str = utils.lat(simp_step.expr_after, ns)
        if step_str != steps_strings[-1]:
            steps_strings.append(step_str)
    changes_s = ' = '.join(steps_strings)
    return changes_s, res


calc = step_by_step_str

# _CONVERT_TEXT = [
#     'И всё выражение превратится в',
#     'Значит, выражение равно',
#     'Отсюда получаем',
#     'Итого выходит',
# ]

has_bracket_re = re.compile(r'\([^) ]* ')


def simplify(expr: str | sympy.Expr, subs_vars: dict | None = None, factor=False, ns=None) -> dict:
    if subs_vars:
        return subs(expr, subs_vars)

    result = {
        'task': expr,
        'sol_codes': [],
    }

    if isinstance(expr, sympy.Expr):
        parsed = expr
        ns = ns or utils.get_num_style(utils.hum(expr))
    else:
        # Для повторных запусков в рамках одной сессии один результат
        # seed(expr)
        try:
            parsed, ns = utils.parse_and_ns(expr)
        except Exception:
            result['error'] = f'Выражение «{expr}» чёт не парсится'
            return result

    if parsed.is_Equality:
        result['sol_codes'].append('simpl-eq')
    elif parsed.is_Relational:
        result['sol_codes'].append('simpl-rel')
    else:
        result['sol_codes'].append('simpl-expr')

    steps = []
    ans = None
    if not parsed.free_symbols:
        result['sol_codes'].append('simpl-no-vars')
        state = school_arithmetics.arithmetics(parsed, steps, ns)
        if state:
            ans = state.ans
            result['sol_codes'].extend(state.sol_codes)
            # Пока не помечаем хорошими.
            if (ans and steps
                    and ('add_whole_and_whole' not in result['sol_codes'] or
                         'add_small_numbers_on_apples' in result['sol_codes'])):
                result['good_scheme'] = True
    if ans is None:
        ans = with_vars(parsed, steps, ns, original=parsed)

    ############################################################
    # Если шагов нет, то сделаем шаг «ничего не сделаешь»
    ############################################################
    if len(steps) == 0:
        if parsed.is_Equality:
            rel_type = 'равенство'
        elif parsed.is_Relational:
            rel_type = 'неравенство'
        else:
            rel_type = 'выражение'
        parsed_s = utils.lat(parsed, ns)
        answer = f'{rel_type.title()} ${parsed_s}$ оставим без изменений'
        steps.append(
            Step(
                action=f'Можно ли как-то упростить {rel_type} ${parsed_s}$?',
                solution=answer,
                answer=answer,
            )
        )
    ############################################################
    # Всё завершаем
    ############################################################
    for i, step in enumerate(steps, start=1):
        result[f'step {i}'] = step

    result['final_answer'] = f'${utils.lat(ans, ns)}$'
    return result


def with_vars(expr: sympy.Expr, steps: list, ns, *, original=None, subs_text=None) -> str:
    simplify_steps, res = step_by_step_and_res(expr, ns)
    res = expr
    # prev_answer_s = None
    for ind, step in enumerate(simplify_steps, start=1):
        before_s = utils.lat(step.before, ns)
        after_s = utils.lat(step.after, ns)
        res = step.expr_after
        expr_after_s = utils.lat(step.expr_after, ns)
        is_rel = step.before.is_Relational and step.after.is_Boolean
        has_vars = len(step.before.free_symbols) > 0
        has_bracket = has_bracket_re.search(before_s)
        if step.change == CHANGE.SubFromBothPartOfRel:
            if step.before.is_Equality:
                rel_type = 'равенство'
            elif step.before.is_Relational:
                rel_type = 'неравенство'
            else:
                rel_type = 'выражение'
            steps.append(
                Step(
                    action=f'Перенесём ${utils.lat(step.before.rhs, ns)}$ из правой части в левую.',
                    solution=(
                        f'Перенесём ${utils.lat(step.before.rhs, ns)}$ из правой части в левую. '
                        f'Для этого вычтем из обеих частей ${utils.lat(step.dif, ns)}$. '
                        f'Получим ${expr_after_s}$.'
                    ),
                    answer=f'${expr_after_s}$',
                )
            )
        elif not is_rel:
            if step.change == CHANGE.CancelRational:
                inst_cmd = 'Сократим дробь'
            elif step.change == CHANGE.CollectNumerAndDenumer:
                inst_cmd = 'Соберём множители в числитель и знаменатель дроби'
            elif step.change == CHANGE.RemoveOnes:
                inst_cmd = 'Уберём множители-единицы в'
            elif step.change == CHANGE.CollectNumer:
                inst_cmd = 'Соберём множители '
            # elif step.change == CHANGE.PowerSimp:
            #     inst_cmd = 'PowerSimp'
            elif step.change == CHANGE.DivInts or step.change == CHANGE.Div:
                inst_cmd = 'Поделим '
            elif step.change == CHANGE.CalcelMuls:
                inst_cmd = 'Перемножим и сократим множители в'
            elif step.change == CHANGE.SqrtDenest:
                inst_cmd = 'Извлечём квадратный корень'
            elif step.change == CHANGE.ExpandMul:
                if has_vars:
                    inst_cmd = 'Раскроем скобки'
                else:
                    inst_cmd = 'Раскроем скобки и вычислим значение выражения'
            elif step.change == CHANGE.DoitMul:
                if has_vars:
                    if '(' in before_s and '(' not in after_s:
                        inst_cmd = 'Раскроем скобки'
                    else:
                        inst_cmd = 'Перемножим все элементы в'
                else:
                    inst_cmd = 'Перемножим все числа в'
            elif step.change == CHANGE.DoitAdd:
                if has_vars:
                    inst_cmd = 'Приведём подобные'
                else:
                    inst_cmd = 'Вычислим сумму'
            elif step.change == CHANGE.DoitPow:
                is_sqrt = step.before.is_Pow and step.before.args[1] == sympy.S.Half
                if has_vars and is_sqrt:
                    inst_cmd = 'Упростим квадратный корень'
                elif has_vars:
                    inst_cmd = 'Упростим степень'
                elif is_sqrt:
                    inst_cmd = 'Вычислим квадратный корень'
                else:
                    inst_cmd = 'Вычислим степень'
            elif has_vars:
                if has_bracket:
                    inst_cmd = 'Раскроем скобки и приведём подобные'
                else:
                    inst_cmd = 'Приведём подобные'
            elif has_bracket:
                inst_cmd = 'Раскроем скобки и вычислим значение выражения'
            else:
                inst_cmd = 'Вычислим значение выражения'
            # finish_act = finish_sol = ''
            # if ind < len(simplify_steps):
            #     where = f'${prev_answer_s}$' if prev_answer_s else 'исходное'
            #     finish_act = f' и подставим в {where}'
            #     finish_sol = f' {choice(_CONVERT_TEXT)} ${expr_after_s}$.'
            steps.append(
                Step(
                    action=f'{inst_cmd} ${before_s}$.',
                    solution=f'{inst_cmd} ${before_s}$, получится ${after_s}$.',
                    answer=f'${after_s}$',
                )
            )
        else:
            # Равенство/неравенство прямо решается
            rel_type = 'равенство' if step.before.is_Equality else 'неравенство'
            verdict = 'выполнено' if step.after else 'не выполнено'
            if subs_text:
                res = f'{rel_type.title()} ${utils.lat(original, ns)}$ при {subs_text} {verdict}'
            else:
                res = f'{rel_type.title()} ${utils.lat(original, ns)}$ {verdict}'
            steps.append(
                Step(
                    action=f'Выполнено ли {rel_type} ${before_s}$?',
                    solution=f'{rel_type.title()} ${before_s}$ {verdict}.',
                    answer=res,
                )
            )
        # prev_answer_s = expr_after_s
    return res


def subs(expr: str, vals: dict) -> dict:
    result = {
        'task': expr,
        'vals': vals,
        'sol_codes': [],
    }
    result['sol_codes'].append('subs')
    try:
        parsed = utils.parse(expr)
    except Exception:
        result['error'] = f'Выражение «{expr}» чёт не парсится'
        return result
    vars = sorted(parsed.free_symbols, key=lambda var: var.name)
    subs_vars = {}
    if len(vals) == 1 and list(vals.keys())[0] == '?':
        if len(vars) == 0:
            result['error'] = f'В выражении «{expr}» нет переменных'
            return result
        if len(vars) > 1:
            result['error'] = f'В выражении «{expr}» больше одной переменной: {", ".join(map(str, vars))}'
            return result
        x = vars.pop()
        subs_vars[x] = utils.parse(vals['?'])
    else:
        try:
            subs_vars = {utils.parse(var): utils.parse(str(val)) for (var, val) in vals.items()}
        except Exception:
            result['error'] = f'«{vals}» чёт не парсится'
            return result
    # Для повторных запусков в рамках одной сессии один результат
    # seed(expr)
    ns = utils.get_num_style(expr + str(vals))
    steps = []
    # Теперь мы распарсили и выражение, и переменные. Упрощаем так
    ans = with_vars(parsed, steps, ns, original=parsed)
    # Может оказаться, что там то подстановки тождество. Тогда игнорируем
    if (
            steps
            and (isinstance(ans, sympy.Expr) and ans.doit().is_Boolean or 'выполнено' in steps[-1]['answer'])
            or sympy.count_ops(ans) >= sympy.count_ops(parsed)
    ):
        steps.clear()
    elif steps:
        parsed = ans
    # Теперь можно сделать обход и подставлять
    try:
        substed = utils.make_subs(parsed, subs_vars)
    except Exception:
        result['error'] = f'В выражение «{expr}» чёт не подставляется «{vals}»'
        return result
    answer_s = '$' + utils.lat(substed, ns) + '$'
    subs_text = ', '.join(f'${x} = {utils.lat(val, ns)}$' for x, val in subs_vars.items())
    vals_text = 'значения' if len(subs_vars) > 1 else 'значение'
    steps.append(
        classes.Step(
            action=f'Подставим в выражение ${utils.lat(parsed, ns)}$ {vals_text} {subs_text}.',
            solution=(
                f'Подставим в выражение ${utils.lat(parsed, ns)}$ {vals_text} {subs_text}. ' f'Получим {answer_s}.'
            ),
            answer=answer_s,
        )
    )

    ans = None
    if not substed.free_symbols:
        state = school_arithmetics.arithmetics(substed, steps, ns)
        if state:
            ans = state.ans
            result['sol_codes'].extend(state.sol_codes)
    if ans is None:
        ans = with_vars(substed, steps, ns, original=parsed, subs_text=subs_text)

    for i, step in enumerate(steps, start=1):
        result[f'step {i}'] = step

    result['final_answer'] = ans if isinstance(ans, str) else '$' + utils.lat(ans, ns) + '$'

    return result


if __name__ == '__main__':
    exprs = [
        # '(x + 3) ^ 2 - x(x + 4)',
        '2,06x - 0,6 x',
        '2+4',
        '2-4',
        '22+44',
        # '0,5 + 2 * 3/4',
        # 'x^2 * x^3',
        # 'x^n * x^3',
        # r'\frac{a ^ {2} + a}{a ^ {2} - 9}',
        # 'a^2 / a^8',
        # '(-2 x)^2',
        # r'\frac{24d^2 c^2}{36ac}',
        # r'(3-2) * 5',
        # r'3**7 * 3**12',
        # r'<<simplify 2x/x^2 >>',
        # r'<<simplify 2*a*b*45 - 3*b*a >>',
        # r'<<simplify 2*a:(b*45) - 3*a/b>>',
        # r'<<simplify 2*a:b*45 - 3*a/b>>',
        # r'<<simplify 2ba - 3 ba>>',
        # r'<<simplify 1/b + 1/(ab)>>',
        # r'<<simplify $0,36a^{-5}b^{6}c^{3} \cdot \left(-2\frac{2}{9}\right)a^{4}b^{-4}c^{-5}$>>'
    ]
    for exp in exprs:
        print('=' * 10)
        print(exp.replace('<', '&lt;').replace('>', '&gt;'))
        print(utils.pprint(simplify(exp.strip('<> simplify'))))
        # print(res_convert.to_text(simplify(exp.strip('<> simplify'))))
