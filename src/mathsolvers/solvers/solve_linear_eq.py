import sympy

from mathsolvers.solvers_stuff import states
from mathsolvers.sympy_stuff import utils

__all__ = ['solve_linear']


def solve_linear(sol: states.SolutionState) -> states.SolutionState:
    """Решить уже «подготовленное» линейное уравнение.
    Необходимая подготовка:
     - домножено на знаменатель, чтобы избавиться от x в знаменателях
     - упрощены левая и правая часть

    Args:
        sol: уже «подготовленное» линейное уравнение.

    Returns:
        В решение добавляются необходимые шаги, а также ответы

    """
    ############################################################
    # Теперь у нас есть все коэффициенты, всё упрощено.
    # Можно переносить переменные из одной части в другую
    ############################################################
    eq = sol.eq
    x = sol.x
    x_s = utils.lat(x)
    ns = sol.ns
    eq.left = eq.left.collect(x)
    eq.right = eq.right.collect(x)
    a1, b1 = eq.left.coeff(x, 1), eq.left.coeff(x, 0)
    a2, b2 = eq.right.coeff(x, 1), eq.right.coeff(x, 0)
    sol.sol_codes.append('eq-linear')
    ############################################################
    # Меняем местами левую и правую часть, если это сразу поможет
    ############################################################
    if a1 == 0 and a2 != 0 and b1 != 0 and b2 == 0:
        eq.swap()
        a1, b1, a2, b2 = a2, b2, a1, b1
        sol.add_step(
            action=f'Поменяем местами левую и правую часть уравнения ${eq.prev_left_s} {eq.op} {eq.prev_right_s}$.',
            solution=f'Сделаем так, чтобы слева были все слагаемые с ${x_s}$, а справа — без. '
                     f'Для этого просто поменяем местами левую и правую часть. '
                     f'Получим ${eq.left_s} = {eq.right_s}$.',
            answer=f'${eq.left_s} = {eq.right_s}$',
        )
        sol.sol_codes.append('eq-lin-swap-left-right')

    ############################################################
    # Переносим x из правой части в левую
    ############################################################
    if a2 != 0:
        term = a2 * x
        term_s = utils.lat(term, ns)
        try:
            a2_is_gt_0 = bool(a2 > 0)
        except Exception:
            a2_is_gt_0 = True
        if a2_is_gt_0:
            eq -= term
            op = f'из обеих частей вычесть ${term_s}$'
            changes = (
                f'${eq.prev_left_s} - {term_s} = {eq.prev_right_s} - {term_s}$\n'
                'После упрощения получаем:\n'
                f'${eq.left_s} = {eq.right_s}$'
            )
        else:
            terms_neg = -a2 * x
            terms_neg_s = utils.lat(terms_neg, ns)
            eq += terms_neg
            op = f'к обеим частям прибавить ${terms_neg_s}$'
            changes = (
                f'${eq.prev_left_s} + {terms_neg_s} = {eq.prev_right_s} + {terms_neg_s}$\n'
                'После упрощения получаем:\n'
                f'${eq.left_s} = {eq.right_s}$'
            )
        sol.add_step(
            action=f'Перенесём ${term_s}$ из правой части в левую.',
            solution=f'Сделаем так, чтобы все слагаемые с ${x_s}$ оказались слева. '
                     f'Перенесём ${term_s}$ из правой части в левую. '
                     f'Для этого нужно {op}:\n{changes}',
            answer=f'${eq.left_s} = {eq.right_s}$',
        )
        sol.sol_codes.append('eq-lin-term-right-to-left')

    ############################################################
    # Переносим свободный член из левой в правую
    ############################################################
    eq.left = eq.left.collect(x)
    a1, b1 = eq.left.coeff(x, 1), eq.left.coeff(x, 0)
    if b1 != 0 and a1 != 0:
        term = b1
        term_s = utils.lat(b1, ns)
        # Вот эта фигня для того, чтобы решать уравнения с параметром
        try:
            coef_b1_is_gt_0 = bool(b1 > 0)
        except TypeError:
            coef_b1_is_gt_0 = True
        if coef_b1_is_gt_0:
            eq -= term
            op = f'из обеих частей вычесть ${term_s}$'
            changes = (
                f'${eq.prev_left_s} - {term_s} = {eq.prev_right_s} - {term_s}$\n'
                'После упрощения получаем:\n'
                f'${eq.left_s} = {eq.right_s}$'
            )
        else:
            terms_neg = -b1
            terms_neg_s = utils.lat(terms_neg, ns)
            eq += terms_neg
            op = f'к обеим частям прибавить ${terms_neg_s}$'
            changes = (
                f'${eq.prev_left_s} + {terms_neg_s} = {eq.prev_right_s} + {terms_neg_s}$\n'
                'После упрощения получаем:\n'
                f'${eq.left_s} = {eq.right_s}$'
            )
        sol.add_step(
            action=f'Перенесём ${utils.lat(term, ns)}$ из левой части в правую.',
            solution=f'Сделаем так, чтобы слева были все слагаемые с ${x_s}$, а справа — без. '
                     f'Перенесём ${term_s}$ из левой части в правую. Для этого нужно {op}:\n{changes}',
            answer=f'${eq.left_s} = {eq.right_s}$',
        )
        sol.sol_codes.append('eq-lin-term-left-to-right')

    ############################################################
    # Теперь переменная слева, числа справа.
    # Сокращаем на коэффициент перед x, если он не 0
    ############################################################
    eq.left = eq.left.collect(x)
    eq.right = eq.right.collect(x)
    a1 = eq.left.coeff(x, 1)
    b1 = eq.left.coeff(x, 0)
    b2 = eq.right.coeff(x, 0)
    bad_parms_values = []
    bad_parm = None
    if a1 == 0 and b1 == 0 and b2 == 0:
        sol.add_step(
            action='Получили уравнение $0 = 0$, какие у него решения?',
            solution=f'У уравнения $0 = 0$ любое значение ${x_s}$ является решением: '
                     f'получилось тождество, которое не зависит от ${x_s}$.',
            answer=f'${x_s}$ — любое',
        )
        sol.sol_codes.append('eq-lin-got-0-0')
        sol.sol = [{x_s: 'R'}]
        sol.final_answer = f'${x_s}$ — любое'
        # TODO — denomenator!
        return sol
    elif a1 == 0:
        sol.add_step(
            action=f'Получили уравнение ${eq.left_s} = {eq.right_s}$, какие у него решения?',
            solution=f'У уравнения ${eq.left_s} = {eq.right_s}$ нет решений, '
                     f'так как и левая, и правая часть не зависят от ${x_s}$, и они не равны друг другу.',
            answer='Корней нет',
        )
        sol.sol_codes.append('eq-lin-got-0-ne-0')
        sol.sol = []
        sol.final_answer = 'Корней нет'
        return sol
    elif a1 == -1:
        eq *= -1
        sol.add_step(
            action='Поменяем знак обеих частей',
            solution=(
                f'Поменяем знаки обеих частей уравнения:\n'
                f'${eq.prev_left_s} = {eq.prev_right_s}$\n'
                f'Получится уравнение\n'
                f'${eq.left_s} = {eq.right_s}$'
            ),
            answer=f'${eq.left_s} = {eq.right_s}$',
        )
        sol.sol_codes.append('eq-lin-chg-sgn')
    elif a1 != 1:
        eq /= a1
        if len(a1.free_symbols) == 1:
            bad_parm = list(a1.free_symbols)[0]
            try:
                bad_parms_values = list(sympy.solve(a1, bad_parm))
            except Exception:
                # TODO Хз, что здесь делать
                pass
        divs = utils.lat(a1, ns)
        # Это для уравнений с параметром
        try:
            coef_a1_is_lt_0 = bool(a1 < 0)
        except TypeError:
            coef_a1_is_lt_0 = False
        divs_b = f'({divs})' if coef_a1_is_lt_0 or '/' in divs else divs
        prev_leftexs_b = f'({eq.prev_left_s})' if '/' in eq.prev_left_s else eq.prev_left_s
        prev_rightexs_b = f'({eq.prev_right_s})' if '/' in eq.prev_right_s else eq.prev_right_s
        sol.add_step(
            action=f'Поделим обе части уравнения на ${divs}$',
            solution=(
                f'Поделим обе части уравнения на ${divs}$.\n'
                f'$\\frac{{{prev_leftexs_b}}}{{{divs_b}}} = \\frac{{{prev_rightexs_b}}}{{{divs_b}}}$\n'
                f'Cлева коэффициент сократится, получится просто ${x_s}$.\n'
                f'После упрощения получаем:\n'
                f'${eq.left_s} = {eq.right_s}$'
            ),
            answer=f'${eq.left_s} = {eq.right_s}$',
        )
        sol.sol_codes.append('eq-lin-div-both')
    sol.final_answer = f'${x_s} = {eq.right_s}$'
    sol.sol = [{x_s: eq.right_s}]
    ############################################################
    # Если уравнения с параметром, то нужно выколоть значения параметра,
    # когда ответ не имеет смысл
    ############################################################
    if bad_parms_values:
        no_root_bads = []
        any_root_bads = []
        for bad_root in bad_parms_values:
            right = eq.prev_right.subs(bad_parm, bad_root).simplify()
            if right == 0:
                any_root_bads.append(bad_root)
            else:
                no_root_bads.append(bad_root)
        bad_parms_joined = ', '.join(utils.lat(bad_root, ns) for bad_root in bad_parms_values)
        bad_parms_no_joined = ', '.join(utils.lat(bad_root, ns) for bad_root in no_root_bads)
        bad_parms_all_joined = ', '.join(utils.lat(bad_root, ns) for bad_root in any_root_bads)
        bad_no_text = bad_all_text = bad_no_ans = bad_all_ans = ''
        if no_root_bads:
            bad_no_text = f'При ${bad_parm} = {bad_parms_no_joined}$ корней у исходного уравнения нет. '
            bad_no_ans = f', при ${bad_parm} = {bad_parms_no_joined}$ корней нет'
        if any_root_bads:
            bad_all_text = f'При ${bad_parm} = {bad_parms_all_joined}$ любое число является корнем. '
            bad_all_ans = f', при ${bad_parm} = {bad_parms_all_joined}$ любое число является корнем'
        try:
            sol.final_answer = f'${x_s} = {eq.right_s}$ при ${bad_parm} ≠ {bad_parms_joined}${bad_no_ans}{bad_all_ans}'
            sol.add_step(
                action=(
                    f'При каких значениях параметра ${bad_parm}$ нельзя делить на ${utils.lat(a1, ns)}$? '
                ),
                solution=(
                    f'При ${bad_parm} = {bad_parms_joined}$ выражение ${utils.lat(a1, ns)}$ равно $0$, '
                    f'и делить на него нельзя. '
                    f'{bad_no_text}{bad_all_text}'
                ),
                answer=f'При ${bad_parm} = {bad_parms_joined}$. {bad_no_text}{bad_all_text}',
            )
            sol.sol_codes.append('eq-lin-rem-parm-roots')
        except Exception:
            # TODO Хз, что здесь делать
            pass

    ############################################################
    # Если мы домножали на знаменатель, то нужно выкинуть его корни
    # TODO: Если в уравнении есть параметры, то нужно выколоть нули знаменателя. Сейчас это не делается
    ############################################################
    if eq.lcm_denom != 1 and eq.lcm_denom.free_symbols:
        root_is_root_of_denom = eq.lcm_denom.subs(x, eq.right).expand().simplify() == 0
        if root_is_root_of_denom:
            sol.sol = []
            sol.final_answer = 'Корней нет'
            sol.add_step(
                action=(
                    f'Проверим, является ли ${x_s} = {eq.right_s}$ корнем знаменателя ${eq.lcm_denom_s}$. '
                ),
                solution=(
                    f'Подставим ${x_s} = {eq.right_s}$ в знаменатель ${eq.lcm_denom_s}$. Получится $0$. '
                    f'Значит число ${eq.right_s}$ является нулём знаменателя '
                    f'и не входит в область определения функции. '
                    f'Поэтому корней у исходного уравнения нет.'
                ),
                answer='Корней нет.',
            )
            sol.sol_codes.append('eq-lin-rem-denom-roots')
    ############################################################
    # Если нет ни одного шага, то у нас было уравнение вида x = 2
    ############################################################
    if len(sol.steps) == 0:
        sol.add_step(
            action=f'Cразу выпишем корни уравнения ${eq}$',
            solution=f'Уравнение ${eq}$ уже решено, его корень равен ${eq.right_s}$.',
            answer=f'${eq.right_s}$',
        )
    if len(eq.vars) == 1 and sol.good_scheme is None:
        # Уравнения с параметрами не рассматриваем
        sol.good_scheme = True
    return sol
