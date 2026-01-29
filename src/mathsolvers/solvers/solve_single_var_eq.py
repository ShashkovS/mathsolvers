import math
from itertools import chain
import sympy

from mathsolvers.solvers import (
    solve_linear_eq,
    solve_quadratic_eq,
    simplification,
)
from mathsolvers.solvers_stuff import states
from mathsolvers.sympy_stuff import utils

__all__ = ['solve_single_var']

replace_ru_tbl = str.maketrans('укегхаросм', 'ykerxapocm')


############################################################
# Решаем уравнения одной переменной
############################################################
def solve_single_var(expr: str, vars: list[str] | None = None) -> states.SolutionState:
    """Решить уравнение одной переменной по шагам.
    В данный момент решаются линейные и квадратные уравнения,
    а также уравнения, уже разложенные на линейные множители
    Args:
        expr: строка с уравнением
        vars: либо пусто, либо список с именем переменной, относительно которой нужно решить уравнение

    Returns:
        класс states.SolutionState, содержащий всю информацию о задаче и её решении

    """
    # Так. В solve у нас не может быть аров, поэтому заменим русские a, x, o на латинские
    expr = expr.translate(replace_ru_tbl)

    sol = states.SolutionState(expr=expr)
    ############################################################
    # Парсим уравнение
    ############################################################
    sol.eq = eq = states.EquationState(expr)
    if eq.error:
        sol.error = eq.error
        return sol
    sol.ns = eq.ns
    ############################################################
    # Парсим переменные, если они переданы
    ############################################################
    if vars:
        try:
            parsed_vars = [utils.parse(x) for x in vars]
        except Exception:
            sol.error = f'Список переменных {vars} не парсится'
            return sol
        if not all(x.is_Symbol for x in parsed_vars):
            sol.error = f'Список переменных {vars} не парсится'
            return sol
        sol.vars = vars = parsed_vars
    ############################################################
    # Проверяем переменные
    ############################################################
    if len(eq.vars) == 0 and len(vars) > 0 and eq.op == '=':
        if eq.diff == 0:
            # Всё — решение
            sol.sol = [{x.name: 'R' for x in vars}]
            sol.sol_codes.append('noeq-sol-r')
            sol.final_answer = '; '.join(f'${x.name}$ — любое' for x in vars)
        else:
            # Решений нет
            sol.sol = []
            sol.sol_codes.append('noeq-sol-none')
            sol.final_answer = 'Корней нет'
        return sol
    if len(eq.vars) == 0:
        sol.error = f'В выражении «{expr}» нет переменных'
        sol.sol_codes.append('noeq-novars')
        return sol
    if vars and len(vars) > 1:
        sol.error = f'Не умеем решать уравнения с несколькими переменными {vars}'
        sol.sol_codes.append('eq-too-many-vars')
        return sol
    sol.x = eq.set_var(vars and vars[0])
    # eq_s_saved = str(eq)
    sol.sol_codes.append(f'eq-parms-{len(eq.vars) - 1}')
    ############################################################
    # Ну, всё готово. Можем решать!
    solve_parsed_single_var_eq(sol)
    # # Временно заземлили эту фичу
    # if not sol.error and len(sol.steps) > 0 and eq.op == '=':
    #     first_action = sol.steps[0]['action']
    #     if first_action:
    #         first_action = first_action[0].lower() + first_action[1:]
    #     first_of_all = ''
    #     if len(sol.steps) > 1:
    #         first_of_all = 'сначала '
    #     new_first_action = f'Для решения уравнения ${eq_s_saved}$ {first_of_all}{first_action}'
    #     sol.steps[0]['action'] = new_first_action
    return sol


############################################################
# Решаем «готовое»
############################################################
def solve_parsed_single_var_eq(sol: states.SolutionState) -> states.SolutionState:
    x = sol.x
    eq = sol.eq
    sol.sol_codes.append('sol-single-var-eq')
    ############################################################
    # Может быть, всё уже разложено?
    ############################################################
    try:
        # degree может падать, если выражение — не многочлен
        only_lin_mul = eq.right == 0 and eq.left.is_Mul and all(sympy.degree(term, x) <= 1 for term in eq.left.args)
    except Exception:
        only_lin_mul = False
    if only_lin_mul and eq.op == '=':
        return case_mul(sol)
    ############################################################
    # Определяем НОК знаменателей, если выражение не является многочленом (не удалось определить степень)
    # При необходимости домножаем на знаменатель, чтобы от него избавиться.
    ############################################################
    try:
        ldeg = sympy.degree(eq.left, eq.x)
    except Exception:
        ldeg = -1
    try:
        rdeg = sympy.degree(eq.right, eq.x)
    except Exception:
        rdeg = -1
    sol.sol_codes.append(f'eq-ldeg-{ldeg}-rdeg-{rdeg}')

    if eq.deg == -1 or ldeg == -1 or rdeg == -1:
        eq.find_denom_and_mul()
        if eq.lcm_denom != 1:
            # Повторный вызов для того, чтобы обновить степень, теперь выражение может стать многочленом
            eq.set_var(x)
            deg_comment = ''
            if eq.deg == 1:
                deg_comment = 'У нас получилось линейное уравнение.'
            elif eq.deg == 2:
                deg_comment = 'У нас получилось квадратное уравнение.'
            elif eq.deg == 3:
                deg_comment = 'У нас получилось кубическое уравнение.'
            elif eq.deg > 3:
                deg_comment = f'У нас получилось уравнение степени {eq.deg}.'
            # Если одновременно и левая, и правая часть сложные, то будем делать домножение в два шага
            if (eq.prev_left != 1 and eq.prev_right != 1
                    and (sympy.count_ops(eq.left) + sympy.count_ops(eq.right) + sympy.count_ops(eq.lcm_denom))) >= 6:
                sol.add_step(
                    action=(
                        f'Домножим левую часть уравнения ${eq.prev_left_s}$ на ${eq.lcm_denom_s}$.'
                    ),
                    solution=(
                        f'Чтобы избавиться от знаменателей в ${eq.prev_left_s}$ и в ${eq.prev_right_s}$, '
                        f'мы можем домножить уравнение на ${eq.lcm_denom_s}$. '
                        f'Сначала домножим левую часть ${eq.prev_left_s}$ и упростим результат:\n'
                        f'${eq.left_changes_sbs}$.\n'
                    ),
                    answer=f'${eq.left_s}$',
                )
                sol.add_step(
                    action=(
                        f'Домножим правую часть уравнения ${eq.prev_right_s}$ на ${eq.lcm_denom_s}$.'
                    ),
                    solution=(
                        f'Домножим правую часть уравнения ${eq.prev_right_s}$ '
                        f'на ${eq.lcm_denom_s}$ и упростим результат.\n'
                        f'${eq.right_changes_sbs}$.\n'
                        f'Наше уравнение превращается в уравнение\n${eq}$.\n'
                        f'{deg_comment}'
                    ),
                    answer=f'${eq.right_s}$',
                )
            else:
                sol.add_step(
                    action=(
                        f'Домножим уравнение ${eq.prev_left_s} = {eq.prev_right_s}$ на ${eq.lcm_denom_s}$.'
                    ),
                    solution=(
                        f'Чтобы избавиться от знаменателей в уравнении ${eq.prev_left_s} = {eq.prev_right_s}$, '
                        f'мы можем домножить его на ${eq.lcm_denom_s}$. '
                        f'Сначала домножим левую часть ${eq.prev_left_s}$:\n'
                        f'${eq.left_changes_sbs}$.\n'
                        f'Теперь домножим правую часть уравнения ${eq.prev_right_s}$:\n'
                        f'${eq.right_changes_sbs}$.\n'
                        f'Наше уравнение превращается в уравнение\n${eq}$.\n'
                        f'{deg_comment}'
                    ),
                    answer=f'${eq}$',
                )
            sol.sol_codes.append('eq-mul-denom')
    # Теперь делаем такой хак. Если все ответы целые, то избавляемся от знаменателей.
    if eq.op == '=' and eq.lcm_denom == 1 and 1 <= eq.deg <= 2:
        all_roots_are_integer = False
        try:
            poly = sympy.Poly(eq.diff, eq.x)
            solutions = sympy.real_roots(poly)
            all_roots_are_integer = all(root.is_Integer for root in solutions)
        except Exception:
            pass
        if all_roots_are_integer:
            eq_prev_s = str(eq)
            eq.find_denom_and_mul(100)
            if eq.lcm_denom != 1:
                sol.add_step(
                    action=(
                        f'Домножим обе части уравнения на ${eq.lcm_denom_s}$ и упростим результат.'
                    ),
                    solution=(
                        'Чтобы было удобнее считать, '
                        f'избавимся от знаменателей в уравнении ${eq_prev_s}$. '
                        f'Для этого домножим уравнение на общий знаменатель левой и правой части ${eq.lcm_denom_s}$. '
                        f'Домножим сначала левую часть:\n${eq.left_changes_sbs}$.\n'
                        f'Теперь домножим правую часть:\n${eq.right_changes_sbs}$\n'
                        f'Наше уравнение превращается в уравнение ${eq}$.'
                    ),
                    answer=f'${eq}$',
                )
                sol.sol_codes.append('eq-mul-num-denom')
    # Пока творим дичь, если перед x есть нецелые коэффициенты...
    try:
        coeffs = sympy.Poly(eq.left - eq.right, eq.x).all_coeffs()
        coeffs.pop()  # Свободный коэффициент можно игнорировать
        if any(not coeff.is_Integer for coeff in coeffs):
            sol.good_scheme = False
    except Exception:
        sol.good_scheme = False

    ############################################################
    # Упрощаем
    ############################################################
    cancel_the_same(sol)
    simplify_step(sol)
    sub_the_same(sol)

    ############################################################
    # Решаем уже «хорошее» уравнение
    ############################################################

    if eq.deg > 2 or eq.op != '=' or eq.deg == -1 or eq.left.has(sympy.Abs) or eq.right.has(sympy.Abs):
        return case_no_step_by_step_sol(sol)
    if 0 <= eq.deg <= 1 or eq.deg.is_infinite:
        return solve_linear_eq.solve_linear(sol)
    if eq.deg == 2:
        return solve_quadratic_eq.solve_quadratic(sol)
    return case_no_step_by_step_sol(sol)


############################################################
# случай вида A(bx+c)(dx+e)...
############################################################
def case_mul(sol: states.SolutionState) -> states.SolutionState:
    sol.sol_codes.append('sol-eq-mul-lin')
    deg0 = []
    deg1 = []
    x = sol.x
    eq = sol.eq
    ns = sol.ns
    for term in eq.left.args:
        if sympy.degree(term, x) == 1:
            deg1.append(term)
        else:
            deg0.append(term)
    part1 = sympy.Mul(*deg1, evaluate=False)
    part1_s = utils.lat(part1, ns)
    if any(el != 1 for el in deg0):
        part0 = sympy.Mul(*deg0, evaluate=False)
        part0_s = utils.lat(part0, ns)
        sol.add_step(
            action=f'Сократим все множители без ${x}$ в уравнении ${eq}$.',
            solution=(
                'Произведение равно нулю тогда и только тогда, когда хотя бы один из множителей равен нулю. '
                f'Поэтому мы можем сократить уравнение на ${part0_s}$, ведь ${part0_s}$ не может быть равно 0. '
                f'Поделим обе части уравнения на ${part0_s}$. '
                f'Получаем уравнение ${part1_s} = 0$.'
            ),
            answer=f'${part1_s} = 0$',
        )
    eq.left = part1
    eqs = None
    for ind, term in enumerate(deg1):
        old_term_s = utils.lat(term, ns)
        term_c = term.collect(x)
        a = term_c.coeff(x, 1)
        b = term_c.coeff(x, 0)
        a_s = utils.lat(a, eq.ns)
        new_b = b / a
        eq.roots.append(-new_b)
        if a == 1:
            continue
        if a == -1:
            term = sympy.Mul(term, -1, evaluate=False)
        else:
            term = sympy.Mul(term, sympy.Pow(a, -1, evaluate=False), evaluate=False)
        # term /= a
        changes, term = simplification.step_by_step_str_and_res(term, eq.ns, fin_simplify=True)
        # term = utils.normalize_terms_order(term.expand())
        deg1[ind] = term
        part1 = sympy.Mul(*deg1, evaluate=False)
        eqs = f'{utils.lat(part1, eq.ns)} = 0'
        new_term_s = utils.lat(term, eq.ns)
        if a == -1:
            sol.add_step(
                action=f'Умножим множитель ${old_term_s}$ на ${a_s}$',
                solution=(
                    f'Чтобы можно было сразу получить корень уравнения ${old_term_s} = 0$, '
                    f'умножим множитель ${old_term_s}$ на ${a_s}$:\n'
                    f'${changes}$\n'
                    f'Множитель превратился в ${new_term_s}$, а уравнение — в ${eqs}$'
                ),
                answer=f'${new_term_s}$',
            )
        elif a != 1:
            sol.add_step(
                action=f'Поделим множитель ${old_term_s}$ на ${a_s}$',
                solution=(
                    f'Чтобы можно было сразу получить корень уравнения ${old_term_s} = 0$, '
                    f'поделим множитель ${old_term_s}$ на ${a_s}$.\n'
                    f'${changes}$\n'
                    f'Множитель превратился в ${new_term_s}$, а уравнение — в ${eqs}$'
                ),
                answer=f'${new_term_s}$',
            )
    eq.roots = list(set(eq.roots))
    try:
        eq.roots.sort(key=lambda root: root.evalf())
    except Exception:
        # Если есть параметр, то корни не отсортируются...
        pass
    roots_s = '; '.join(f'{x} = {utils.lat(root, eq.ns)}' for root in eq.roots)
    eqs_s = ', '.join(f'${x} - {utils.lat(root, eq.ns)} = 0$' for root in eq.roots)
    if eqs is None:
        eqs = f'{utils.lat(part1, eq.ns)} = 0'
    # eqs обязательно определён в цикле выше
    if len(sol.steps) > 0:
        action = f'Теперь выпишем все корни уравнения ${eqs}$.'
    else:
        action = f'Сразу выпишем все его корни уравнения ${eqs}$.'
    sol.add_step(
        action=action,
        solution=(
            f'${eqs}$ тогда и только тогда, когда один из множителей равен 0. '
            f'Поэтому корни этого уравнения — в точности корни всех уравнений {eqs_s}. '
            f'Выпишем эти корни: ${roots_s}$'
        ),
        answer=f'${roots_s}$',
    )
    sol.sol = [{utils.lat(x): utils.lat(root, eq.ns)} for root in eq.roots]
    sol.final_answer = f'${roots_s}$'
    if len(eq.vars) == 1 and sol.good_scheme is None:
        # Уравнения с параметрами не рассматриваем
        sol.good_scheme = True
    return sol


############################################################
# Упрощаем левую и правую часть
############################################################
def simplify_step(sol: states.SolutionState):
    eq = sol.eq
    eq.simplify()
    if utils.has_significant_change(eq.left, eq.prev_left, eq.ns):
        has_vars = len(eq.left.free_symbols) > 0
        has_bracket = '(' in eq.prev_left_s
        if has_vars:
            if has_bracket:
                instruct = 'раскроем скобки и приведём подобные'
            else:
                instruct = 'приведём подобные'
        elif has_bracket:
            instruct = 'раскроем скобки и вычислим значение выражения'
        else:
            instruct = 'вычислим значение выражения'
        sol.add_step(
            action=f'Упростим левую часть ${eq.prev_left_s}$ уравнения.',
            solution=(
                f'Упростим левую часть ${eq.prev_left_s}$: {instruct}. '
                f'Получаем ${eq.left_changes_sbs}$. '
                f'Наше уравнение превращается в уравнение ${eq.left_s} = {eq.prev_right_s}$.'
            ),
            answer=f'${eq.left_s}$',
        )
        sol.sol_codes.append('eq-simpl-left')
    if utils.has_significant_change(eq.right, eq.prev_right, eq.ns):
        has_vars = len(eq.right.free_symbols) > 0
        has_bracket = '(' in eq.prev_right_s
        # TODO Бе-е-е-е
        if has_vars:
            if has_bracket:
                instruct = 'раскроем скобки и приведём подобные'
            else:
                instruct = 'приведём подобные'
        elif has_bracket:
            instruct = 'раскроем скобки и вычислим значение выражения'
        else:
            instruct = 'вычислим значение выражения'
        sol.add_step(
            action=f'Упростим правую часть ${eq.prev_right_s}$ уравнения.',
            solution=(
                f'Упростим правую часть ${eq.prev_right_s}$: {instruct}. '
                f'Получаем ${eq.right_changes_sbs}$. '
                f'Наше уравнение превращается в уравнение ${eq}$.'
            ),
            answer=f'${eq}$',
        )
        sol.sol_codes.append('eq-simpl-right')


############################################################
# Сокращаем лишнее
############################################################
def sub_the_same(sol: states.SolutionState):
    eq = sol.eq
    if eq.deg == -1 or eq.left == 0:
        return
    # TODO подумать про случай, когда степень не считается (почему-то)
    try:
        left_deg = sympy.degree(eq.left)
    except Exception:
        left_deg = eq.deg
    cmp_deg = eq.deg
    if cmp_deg < 0:  # уравнение 0=0, степень -бесконечность
        cmp_deg = -1
    if left_deg.is_Integer and left_deg > cmp_deg:
        eq.left.collect(eq.x)
        cross_terms = [
            eq.left.coeff(eq.x, i) * (sympy.Pow(eq.x, i, evaluate=False) if i != 1 else eq.x)
            for i in range(left_deg, cmp_deg, -1)
        ]
        term = sympy.Add(*cross_terms, evaluate=False)
        term_s = utils.lat(term, eq.ns)
        try:
            term_is_gt_0 = bool(term > 0)
        except Exception:
            term_is_gt_0 = True
        if term_is_gt_0:
            eq -= term
            op = f'Из обеих частей вычтем ${term_s}$'
            changes = (
                f'${eq.prev_left_s} - {term_s} = {eq.prev_right_s} - {term_s}$\n'
                f'В итоге получается:\n'
                f'${eq.left_s} = {eq.right_s}$'
            )
        else:
            terms_neg = -term
            terms_neg_s = utils.lat(terms_neg, eq.ns)
            eq += terms_neg
            op = f'К обеим частям прибавим ${terms_neg_s}$'
            changes = (
                f'${eq.prev_left_s} + {terms_neg_s} = {eq.prev_right_s} + {terms_neg_s}$\n'
                f'В итоге получается:\n'
                f'${eq.left_s} = {eq.right_s}$'
            )
        sol.add_step(
            action=f'Сократим ${term_s}$ из обеих частей уравнения.',
            solution=f'{op}, тогда ${term_s}$ сократится:\n{changes}',
            answer=f'${eq.left_s} = {eq.right_s}$',
        )
        sol.sol_codes.append('eq-sub-same')


############################################################
# Сокращаем общие числовые множители
############################################################
def cancel_the_same(sol: states.SolutionState):
    eq = sol.eq
    if eq.left == 0 or eq.right == 0:
        return
    # Сначала собираем все слагаемые
    if eq.left.is_Add:
        left_terms = list(eq.left.args)
    else:
        left_terms = [eq.left]
    if eq.right.is_Add:
        right_terms = list(eq.right.args)
    else:
        right_terms = [eq.right]
    if not left_terms or not right_terms:
        return
    # Теперь если каждое слагаемое --- либо Mul, либо число, то добываем из него множители-числа
    numbers = []
    for term in chain(left_terms, right_terms):
        if term.is_Mul:
            nums = [m for m in term.args if m.is_Integer]
            if not nums:
                return
            numbers.append(sympy.Mul(*nums, evaluate=True))
        elif term.is_Integer:
            numbers.append(term)
        else:
            return
    gc = math.gcd(*numbers)
    if gc == 1:
        return
    gc = sympy.sympify(gc)
    # Теперь нам нужно очень аккуратно сократить эти числовые множители
    for x_terms in left_terms, right_terms:
        for ind, term in enumerate(x_terms):
            if term.is_Integer:
                x_terms[ind] = term / gc
            elif term.is_Mul:
                nums = [m for m in term.args if m.is_Integer]
                non_nums = [m for m in term.args if not m.is_Integer]
                canceled = sympy.Mul(*nums) / gc
                if canceled != 1:
                    x_terms[ind] = sympy.Mul(canceled, *non_nums, evaluate=False)
                else:
                    x_terms[ind] = sympy.Mul(*non_nums, evaluate=False)
    eq_prev_s = str(eq)
    eq.left = sympy.Add(*left_terms, evaluate=False)
    eq.right = sympy.Add(*right_terms, evaluate=False)
    eq.diff /= gc
    eq.left_s = utils.lat(eq.left, eq.ns)
    eq.right_s = utils.lat(eq.right, eq.ns)
    sol.add_step(
        action=f'Поделим каждое слагаемое уравнения ${eq_prev_s}$ на ${gc}$.',
        solution=f'Для удобства сократим общий целочисленный множитель всех слагаемых, равный ${gc}$. '
                 f'Каждое слагаемое уравнения поделим на ${gc}$. '
                 f'Получится уравнение ${eq.left_s} = {eq.right_s}$.',
        answer=f'${eq.left_s} = {eq.right_s}$',
    )
    sol.sol_codes.append('eq-cancel-same')


############################################################
# Уравнение не сводящееся к многочлену
############################################################
OP_DECODER = {
    '>': sympy.Gt,
    '>=': sympy.Ge,
    '<': sympy.Lt,
    '<=': sympy.Le,
}


def case_no_step_by_step_sol(sol: states.SolutionState) -> states.SolutionState:
    eq = sol.eq
    x = sol.x
    if eq.op == '=':
        try:
            solutions = sympy.solveset(sympy.Eq(eq.left, eq.right), sol.x, domain=sympy.S.Reals)
        except Exception:
            sol.error = f'Не получается решить уравнение ${eq}$'
            return sol
        solutions_s = utils.lat(solutions, eq.ns)
        sol.add_step(
            action=f'Решим уравнение ${eq}$',
            solution=(f'Решим уравнение ${eq}$.\n' f'Получим множество решений ${solutions_s}$.'),
            answer=f'${x} \\in {solutions_s}$',
        )
        sol.sol_codes.append(f'eq-unknown-deg-{eq.deg}')
    else:
        ineq = OP_DECODER[eq.op](eq.left, eq.right, evaluate=False)
        ineq_s = utils.lat(ineq, eq.ns)
        try:
            solutions = sympy.solve_univariate_inequality(ineq, x, relational=False, domain=sympy.S.Reals)
        except Exception:
            sol.error = f'Не получается решить неравенство ${ineq_s}$'
            return sol
        solutions_s = utils.lat(solutions, eq.ns)
        sol.add_step(
            action=f'Решим неравенство ${ineq_s}$',
            solution=(f'Решим неравенство ${ineq_s}$.\n' f'Получим множество решений ${solutions_s}$.'),
            answer=f'${x} \\in {solutions_s}$',
        )
        sol.sol_codes.append('uneq-unknown')
    sol.final_answer = f'${x} \\in {solutions_s}$'
    sol.good_scheme = False
    return sol

############################################################
