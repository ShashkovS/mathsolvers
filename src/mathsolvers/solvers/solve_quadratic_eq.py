import sympy

from mathsolvers.solvers import simplification
from mathsolvers.solvers_stuff import states
from mathsolvers.sympy_stuff import utils

__all__ = ['solve_quadratic']


def solve_quadratic(sol: states.SolutionState) -> states.SolutionState:
    """Решить уже «подготовленное» квадратное уравнение.
    Необходимая подготовка:
     - домножено на знаменатель, чтобы избавиться от x в знаменателях
     - упрощены левая и правая часть

    Args:
        sol: уже «подготовленное» квадратное уравнение.

    Returns:
        В решение добавляются необходимые шаги, а также ответы

    """
    sol.sol_codes.append('eq-quadratic')
    ############################################################
    # Поймём, что делать с уравнением. Возможны сведения к
    # а) x² = c
    # б) x(x-b) = 0
    # в) ax² + bx + c = 0
    # г) (ab + b)^2 = c
    ############################################################
    eq = sol.eq
    x = sol.x
    x_s = utils.lat(x)
    # случай (ab + b)^2 = c
    try:
        is_case_d = (
            (
                eq.left.is_Pow and eq.left.args[1] == 2 and not eq.right.free_symbols
                and sympy.degree(eq.left.args[0], x) == 1
            )
            or
            (
                eq.right.is_Pow and eq.right.args[1] == 2 and not eq.left.free_symbols
                and sympy.degree(eq.right.args[0], x) == 1
            )
        )
    except Exception:
        is_case_d = False
    if is_case_d:
        # Пока плохая схема
        sol.good_scheme = False
    #     case_d(sol)
    # else:
    eq.diff = eq.diff.expand().collect(x)  # Без явного вызова collect вызовы .coeff могут лажать
    b, c = eq.diff.coeff(x, 1), eq.diff.coeff(x, 0)
    if b == 0:  # а) x² = c
        case_a(sol)
    elif c == 0:  # б) x(x-b) = 0
        case_b(sol)
    else:  # в) ax² + bx + c = 0
        case_c(sol)

    ############################################################
    # Если мы домножали на знаменатель, то нужно выкинуть его корни
    ############################################################
    remove_denom_roots(sol)

    ############################################################
    # Всё завершаем
    ############################################################
    if not sol.eq.roots:
        sol.final_answer = 'Корней нет'
        sol.sol = []
    else:
        sol.sol = [{utils.lat(x): utils.lat(root, eq.ns)} for root in sol.eq.roots]
        sol.final_answer = '$' + '; '.join(f'{x_s} = {utils.lat(root, eq.ns)}' for root in sol.eq.roots) + '$'

    if len(eq.vars) == 1 and sol.good_scheme is None:
        # Уравнения с параметрами не рассматриваем
        sol.good_scheme = True
    return sol


# случай а) x² = c
############################################################
def case_a(sol: states.SolutionState):
    eq = sol.eq
    x = sol.x
    x_s = utils.lat(x)
    sol.sol_codes.append('eq-quadr-x^2=c')
    ############################################################
    # Переносим x² из правой части в левую
    ############################################################
    a2 = eq.right.collect(x).coeff(x, 2)
    if a2 != 0:
        term = a2 * x ** 2
        term_s = utils.lat(term, eq.ns)
        eq -= term
        # Вот эта фигня для того, чтобы решать уравнения с параметром
        try:
            coef_a2_is_gt = bool(a2 > 0)
        except TypeError:
            coef_a2_is_gt = True
        if coef_a2_is_gt:
            todo = f'из обеих частей вычтем ${term_s}$'
        else:
            term_neg_s = utils.lat(-term, eq.ns)
            todo = f'к обеим частям прибавим ${term_neg_s}$'
        sol.add_step(
            action=f'Перенесём ${term_s}$ из правой части в левую. Для этого {todo} и приведём подобные.',
            solution=(
                f'Сделаем так, чтобы все слагаемые с ${x_s}^2$ были слева. '
                f'Перенесём ${term_s}$ из правой части в левую. '
                f'Для этого {todo} и приведём подобные.\n'
                f'Слева будет ${eq.left_changes_sbs}$.\n'
                f'Справа — ${eq.right_changes_sbs}$.\n'
                f'Получаем квадратное уравнение ${eq}$'
            ),
            answer=f'${eq}$',
        )
        sol.sol_codes.append('eq-quadr-right-to-left')

    ############################################################
    # Сокращаем части с x
    ############################################################
    b2 = eq.right.collect(x).coeff(x, 1)
    if b2 != 0:
        term = b2 * x
        term_s = utils.lat(term, eq.ns)
        eq -= term
        sol.add_step(
            action=f'Сократим ${term_s}$ из обеих частей уравнения.',
            solution=f'Сократим одинаковый с обеих сторон член ${term_s}$. Получаем квадратное уравнение ${eq}$',
            answer=f'${eq}$',
        )
        sol.sol_codes.append('eq-quadr-cross-x')

    ############################################################
    # Переносим свободный член из левой в правую
    ############################################################
    c1 = eq.left.collect(x).coeff(x, 0)
    if c1 != 0:
        term = c1
        term_s = utils.lat(term, eq.ns)
        eq -= term
        # Вот эта фигня для того, чтобы решать уравнения с параметром
        try:
            coef_c1_is_gt = bool(c1 > 0)
        except TypeError:
            coef_c1_is_gt = True
        if coef_c1_is_gt:
            todo = f'из обеих частей вычтем ${term_s}$'
        else:
            term_neg_s = utils.lat(-term, eq.ns)
            todo = f'к обеим частям прибавим ${term_neg_s}$'
        sol.add_step(
            action=f'Перенесём ${term_s}$ из левой части в правую. Для этого {todo}.',
            solution=(
                f'Сделаем так, чтобы все слагаемые без ${x_s}$ были справа. '
                f'Перенесём ${term_s}$ из левой части в правую. '
                f'Для этого {todo}.\n'
                f'Слева будет ${eq.left_changes_sbs}$.\n'
                f'Справа — ${eq.right_changes_sbs}$.\n'
                f'Получаем квадратное уравнение ${eq}$'
            ),
            answer=f'${eq}$',
        )
        sol.sol_codes.append('eq-quadr-left-to-right')

    ############################################################
    # Убираем коэффициент перед x²
    ############################################################
    a1 = eq.left.collect(x).coeff(x, 2)
    if a1 == -1:
        eq *= -1
        sol.add_step(
            action=f'Поменяем знаки обеих частей уравнения ${eq.prev_left_s} = {eq.prev_right_s}$.',
            solution=(
                f'Поменяем знаки обеих частей уравнения ${eq.prev_left_s} = {eq.prev_right_s}$.\n'
                f'Получаем квадратное уравнение ${eq}$'
            ),
            answer=f'${eq}$',
        )
        sol.sol_codes.append('eq-quadr-change-sgn')
    elif a1 != 1:
        eq /= a1
        a1_s = utils.lat(a1, eq.ns)
        sol.add_step(
            action=f'Поделим обе части уравнения на ${a1_s}$.',
            solution=(
                f'Поделим обе части уравнения на ${a1_s}$.\n'
                f'Слева будет ${eq.left_changes_sbs}$.\n'
                f'Справа — ${eq.right_changes_sbs}$.\n'
                f'Получаем квадратное уравнение ${eq}$'
            ),
            answer=f'${eq}$',
        )
        sol.sol_codes.append('eq-quadr-div-both')

    ############################################################
    # Получаем корни
    ############################################################
    c2 = eq.right.collect(x).coeff(x, 0)
    if c2 == 0:
        eq.roots.append(sympy.S.Zero)
        sol.add_step(
            action=f'Теперь выпишем все корни уравнения ${eq}$',
            solution=f'У уравнения ${eq}$ единственный корень — ${x_s} = 0$.',
            answer=f'${x_s} = 0$',
        )
        sol.sol_codes.append('eq-quadr-x=0')
    else:
        try:
            coef_c2_is_gt = bool(c2 > 0)
        except TypeError:
            coef_c2_is_gt = True
        if coef_c2_is_gt:
            c2_sqrt = sympy.sqrt(c2, evaluate=False)
            c2_sqrt_s = utils.lat(c2_sqrt, eq.ns)
            c2_sqrt_simp = c2_sqrt.simplify()
            c2_sqrt_simp_s = utils.lat(c2_sqrt_simp, eq.ns)
            if 'sqrt' in c2_sqrt_simp_s and c2.is_Rational and c2.q == 10:
                # Десятичные числа, не являющиеся полными квадратами, не упрощаем
                c2_sqrt_simp = c2_sqrt
                c2_sqrt_simp_s = c2_sqrt_s
            eq.roots.append(-c2_sqrt_simp)
            eq.roots.append(c2_sqrt_simp)
            c2_s = utils.lat(c2, eq.ns)
            if utils.has_significant_change(c2_sqrt, c2_sqrt_simp, eq.ns):
                # Корень из дискриминанта можно упростить
                no_sqrt = 'sqrt' not in c2_sqrt_simp_s
                if no_sqrt:
                    sol.add_step(
                        action=(
                            f'Извлечём квадратный корень из ${c2_s}$.'
                        ),
                        solution=(
                            f'У нас получилось квадратное уравнение вида ${x_s}^2 = c$. '
                            f'Если представить $c={c2_s}$ как полный квадрат, то будет легко выписать его корни. '
                            f'Извлечём квадратный корень из ${c2_s}$, получим\n'
                            f'${c2_sqrt_s} = {c2_sqrt_simp_s}$'
                        ),
                        answer=f'${c2_sqrt_simp_s}$',
                    )
                else:
                    sol.add_step(
                        action=f'Вынесем все множители полные квадраты из ${c2_sqrt_s}$.',
                        solution=(
                            f'У нас получилось квадратное уравнение вида ${x_s}^2 = c$. '
                            f'Если представить $c={c2_s}$ как полный квадрат, то будет легко выписать его корни. '
                            f'${c2_s}$ не является полным квадратом, '
                            f'но немного упростить ${c2_sqrt_s}$ мы можем. '
                            f'Вынесем множители, являющиеся полными квадратами, из ${c2_sqrt_s}$, получим\n'
                            f'${c2_sqrt_s} = {c2_sqrt_simp_s}$'
                        ),
                        answer=f'${c2_sqrt_simp_s}$',
                    )
            sol.add_step(
                action=f'Выпишем корни уравнения ${x_s}^2 = {c2_s}$?',
                solution=(
                    f'Запишем уравнение ${x_s}^2 = {c2_s}$ в виде ${x_s}^2 = ({c2_sqrt_simp_s})^2$. '
                    f'У него ровно два корня:\n'
                    f'${x_s} = {c2_sqrt_simp_s}$ и ${x_s} = -{c2_sqrt_simp_s}$'
                ),
                answer=f'${x_s} = {c2_sqrt_simp_s}$; ${x_s} = -{c2_sqrt_simp_s}$',
            )
            sol.sol_codes.append('eq-quadr-x=±c')
        else:
            sol.add_step(
                action=f'Есть ли у уравнения ${eq}$ корни?',
                solution=f'У уравнения ${eq}$ нет корней, так как ${eq.right_s}$ не может быть квадратом числа.',
                answer='Корней нет.',
            )
            sol.sol_codes.append('eq-quadr-no-roots')


############################################################
# случай б) x(x-b) = 0
############################################################
def case_b(sol: states.SolutionState):
    eq = sol.eq
    x = sol.x
    x_s = utils.lat(x)
    sol.sol_codes.append('eq-quadr-x(x-b)')
    if eq.right != 0:
        eq -= eq.right
        sol.add_step(
            action=f'Перенесём всю правую часть ${eq.prev_right_s}$ налево. ',
            solution=(
                f'Перенесём всю правую часть ${eq.prev_right_s}$ налево. '
                f'Для этого из левой части ${eq.prev_left_s}$ вычтем ${eq.prev_right_s}$ и приведём подобные.\n'
                f'Получаем уравнение ${eq.left_changes_sbs} = 0$'
            ),
            answer=f'${eq}$',
        )
        sol.sol_codes.append('eq-quadr-right-to-left')
    a1 = eq.left.collect(x).coeff(x, 2)
    if a1 == -1:
        eq *= -1
        sol.add_step(
            action=f'Поменяем знаки обеих частей уравнения ${eq.prev_left_s} = {eq.prev_right_s}$.',
            solution=(
                f'Поменяем знаки обеих частей уравнения ${eq.prev_left_s} = {eq.prev_right_s}$.\n'
                f'Получаем квадратное уравнение ${eq}$'
            ),
            answer=f'${eq}$',
        )
        sol.sol_codes.append('eq-quadr-change-sgn')
    elif a1 != 1:
        eq /= a1
        a1_s = utils.lat(a1, eq.ns)
        sol.add_step(
            action=f'Поделим обе части уравнения на ${a1_s}$.',
            solution=f'Чтобы коэффициент перед ${x_s}^2$ стал равен $1$, поделим обе части уравнения на ${a1_s}$.\n'
                     f'Получаем ${eq.left_changes_sbs} = 0$.',
            answer=f'${eq}$',
        )
        sol.sol_codes.append('eq-quadr-div-both')
    # сейчас имеем x² + bx = 0. b точно не 0
    b1 = eq.left.collect(x).coeff(x, 1)
    eq._upd_prev()
    eq.left = sympy.Mul(x, sympy.Add(x, b1, evaluate=False), evaluate=False)
    eq.left_s = utils.lat(eq.left, eq.ns)
    eq.left_changes_sbs = f'{eq.prev_left_s} = {eq.left_s}'
    sol.add_step(
        action=f'В левой части ${eq.prev_left_s}$ вынесем ${x_s}$ за скобки.',
        solution=(
            f'Чтобы представить левую часть как произведение, вынесем ${x_s}$ в ${eq.prev_left_s}$ за скобки. '
            f'Получим\n'
            f'${eq.left_changes_sbs} = 0$'
        ),
        answer=f'${eq}$',
    )
    sol.sol_codes.append('eq-quadr-x(..)')
    sol.eq.roots.append(0)
    sol.eq.roots.append(-b1)
    try:
        sol.eq.roots.sort()
    except Exception:
        pass
    mb1s = utils.lat(-b1, eq.ns)
    sol.add_step(
        action=f'Теперь выпишем все корни уравнения ${eq}$',
        solution=f'${eq}$ тогда и только тогда, когда один из множителей равен $0$. '
                 f'Значит, у уравнения ${eq}$ два корня: ${x_s} = 0$ и ${x_s} = {mb1s}$',
        answer=f'${x_s} = 0$; ${x_s} = {mb1s}$',
    )
    sol.sol_codes.append('eq-quadr-write-roots')


############################################################
# случай в) ax² + bx + c = 0
############################################################
def case_c(sol: states.SolutionState):
    eq = sol.eq
    x = sol.x
    x_s = utils.lat(x)
    sol.sol_codes.append('eq-quadr-discr')
    ############################################################
    # Переносим всё справа налево
    ############################################################
    if eq.right != 0:
        eq -= eq.right
        sol.add_step(
            action=f'Перенесём всю правую часть ${eq.prev_right_s}$ налево.',
            solution=(
                f'Перенесём всю правую часть ${eq.prev_right_s}$ налево. '
                f'Из левой части ${eq.prev_left_s}$ вычтем ${eq.prev_right_s}$ и приведём подобные.\n'
                f'Получаем ${eq.left_changes_sbs} = 0$'
            ),
            answer=f'${eq}$',
        )
        sol.sol_codes.append('eq-quadr-right-to-left')

    ############################################################
    # Делаем коэффициент перед x² положительным
    ############################################################
    cl = eq.left.collect(x)
    a1, b1, c1 = cl.coeff(x, 2), cl.coeff(x, 1), cl.coeff(x, 0)
    # Это для уравнений с параметром
    try:
        coef_a1_is_lt_0 = bool(a1 < 0)
    except TypeError:
        coef_a1_is_lt_0 = False
    if coef_a1_is_lt_0:
        eq_bef_s = str(eq)
        eq *= -1
        sol.add_step(
            action=f'Домножим уравнение ${eq_bef_s}$ на $-1$.',
            solution=(f'Для удобства поменяем знак у всех коэффициентов уравнения ${eq_bef_s}$.'
                      f'Умножим всё на $-1$. Получим уравнение\n ' f'${eq.left_changes_sbs} = 0$'),
            answer=f'${eq}$',
        )
        sol.sol_codes.append('eq-quadr-change-sgn')
        cl = eq.left.collect(x)
        a1, b1, c1 = cl.coeff(x, 2), cl.coeff(x, 1), cl.coeff(x, 0)

    ############################################################
    # Считаем дискриминант
    ############################################################
    eq.left_s = utils.lat(utils.normalize_terms_order(eq.left))  # после collect порядок испорчен
    discriminant = sympy.Add(sympy.Pow(b1, 2, evaluate=False), sympy.Mul(-1, 4, a1, c1, evaluate=False), evaluate=False)
    changes, discriminant = simplification.step_by_step_str_and_res(discriminant, eq.ns, fin_simplify=True)
    discriminant = discriminant.simplify()
    discriminant_s = utils.lat(discriminant, eq.ns)
    sol.add_step(
        action=f'Вычислим дискриминант многочлена ${eq.left_s}$.',
        solution=f'Вычислим дискриминант многочлена ${eq.left_s}$. '
                 'Он считается по формуле $b^2 - 4ac$. '
                 f'В нашем случае $a={a1}$, $b={b1}$ и $c={c1}$. '
                 f'Получается так:'
                 f'\n${changes}$',
        answer=f'${discriminant_s}$',
    )
    sol.sol_codes.append('eq-quadr-calc-discr')
    # Это для уравнений с параметром
    try:
        discriminant_is_lt_0 = bool(discriminant < 0)
    except TypeError:
        discriminant_is_lt_0 = False

    if discriminant == 0:
        root = sympy.Mul(-b1, sympy.Pow(sympy.Mul(2, a1, evaluate=False), -1, evaluate=False), evaluate=False)
        changes, root = simplification.step_by_step_str_and_res(root, eq.ns, fin_simplify=True)
        sol.eq.roots.append(root)
        root_s = utils.lat(root, eq.ns)
        sol.add_step(
            action=(
                f'Дискриминант многочлена ${eq.left_s}$ равен $0$. Теперь найдём корень уравнения ${eq}$.'
            ),
            solution=(
                f'Дискриминант многочлена ${eq.left_s}$ равен $0$. '
                f'Значит корень всего один. Он считается по формуле $\\frac{{-b}}{{2a}}$:\n'
                f'В нашем случае $a={a1}$, $b={b1}$.\n'
                f'${changes}$.\n'
                f'Значит у уравнения единственный корень ${x_s} = {root_s}$'
            ),
            answer=f'${x_s} = {root_s}$',
        )
        sol.sol_codes.append('eq-quadr-discr=0')
    elif discriminant_is_lt_0:
        sol.add_step(
            action=f'Дискриминант ${discriminant_s}$ отрицательный. Есть ли у уравнения ${eq}$ корни?',
            solution=f'У уравнения ${eq}$ нет корней, так как дискриминант ${discriminant_s}$ отрицателей.',
            answer='Корней нет.',
        )
        sol.sol_codes.append('eq-quadr-discr<0')
    else:
        discriminant_sqrt = sympy.sqrt(discriminant, evaluate=False)
        discriminant_sqrt_s = utils.lat(discriminant_sqrt, eq.ns)
        discriminant_sqrt_simp = sympy.sqrt(sympy.factor(discriminant), evaluate=True).simplify()
        discriminant_sqrt_simp_s = utils.lat(discriminant_sqrt_simp, eq.ns)
        if 'sqrt' in discriminant_sqrt_simp_s and discriminant.is_Rational and discriminant.q == 10:
            # Десятичные числа, не являющиеся полными квадратами, не упрощаем
            discriminant_sqrt_simp = discriminant_sqrt
            discriminant_sqrt_simp_s = discriminant_sqrt_s

        if utils.has_significant_change(discriminant_sqrt, discriminant_sqrt_simp, eq.ns):
            # Корень из дискриминанта можно упростить
            no_sqrt = 'sqrt' not in utils.lat(discriminant_sqrt_simp)
            if no_sqrt:
                sol.add_step(
                    action=f'Извлечём квадратный корень из дискриминанта ${discriminant_s}$.',
                    solution=(
                        f'Дискриминант равен ${discriminant_s}$. '
                        f'Чтобы посчитать корни, '
                        f'нам нужно вычислить квадратный корень из дискриминанта ${discriminant_s}$. '
                        f'Извлечём квадратный корень, получим\n'
                        f'${discriminant_sqrt_s} = {discriminant_sqrt_simp_s}$'
                    ),
                    answer=f'${discriminant_sqrt_simp_s}$',
                )
            else:
                sol.add_step(
                    action=f'Вынесем все множители полные квадраты из ${discriminant_sqrt_s}$.',
                    solution=(
                        f'Дискриминант равен ${discriminant_s}$, что не является полным квадратом. '
                        f'Вынесем из-под корня множители, являющиеся полными квадратами. Получим\n'
                        f'${discriminant_sqrt_s} = {discriminant_sqrt_simp_s}$'
                    ),
                    answer=f'${discriminant_sqrt_simp_s}$',
                )
        x1 = sympy.Mul(
            sympy.Add(-b1, -discriminant_sqrt_simp, evaluate=False),
            sympy.Pow(sympy.Mul(2, a1, evaluate=False), -1, evaluate=False),
            evaluate=False,
        )
        x2 = sympy.Mul(
            sympy.Add(-b1, discriminant_sqrt_simp, evaluate=False),
            sympy.Pow(sympy.Mul(2, a1, evaluate=False), -1, evaluate=False),
            evaluate=False,
        )
        for root, root_name, root_ind, sgn in (x1, 'меньший', '_1', '-'), (x2, 'второй', '_2', '+'):
            changes, root = simplification.step_by_step_str_and_res(root, eq.ns, fin_simplify=True)
            sol.eq.roots.append(root)
            roots = utils.lat(root, eq.ns)
            sol.add_step(
                action=f'Корень из дискриминанта равен ${discriminant_sqrt_simp_s}$. '
                       f'Вычислим {root_name} корень уравнения ${eq}$.',
                solution=(
                    f'Корень из дискриминанта равен ${discriminant_sqrt_simp_s}$. '
                    f'Вычислим {root_name} корень уравнения ${eq}$ '
                    f'по формуле $\\frac{{-b {sgn} \\sqrt{{D}}}}{{2a}}$. '
                    f'В нашем случае $a={a1}$, $b={b1}$ и $c={c1}$. '
                    f'Получается так:'
                    f'${changes}$\n'
                    f'Значит {root_name} корень ${x_s}{root_ind}$ равен ${roots}$'
                ),
                answer=f'${roots}$',
            )
        sol.sol_codes.append('eq-quadr-calc-roots-with-discr')


############################################################
# случай d) (ax+b)² = c
############################################################
def case_d(sol: states.SolutionState):
    # eq = sol.eq
    # x = sol.x
    # x_s = utils.lat(x)
    sol.sol_codes.append('eq-quadr-(ax+b)^2=c')


############################################################
# обрабатываем корни знаменателя, на который мы домножили
############################################################
def remove_denom_roots(sol: states.SolutionState):
    eq = sol.eq
    x = sol.x
    # x_s = utils.lat(x)
    if sol.eq.lcm_denom != 0 and sol.eq.lcm_denom != 1 and sol.eq.lcm_denom.free_symbols:
        bad_roots = []
        any_root_is_root_of_denom = False
        for ind in range(len(sol.eq.roots) - 1, -1, -1):
            root = sol.eq.roots[ind]
            root_is_root_of_denom = sol.eq.lcm_denom.subs(x, root).expand().simplify() == 0
            if root_is_root_of_denom:
                bad_roots.append(root)
                any_root_is_root_of_denom = True
                sol.eq.roots.pop(ind)
        if any_root_is_root_of_denom:
            bad_roots_s = ', '.join(utils.lat(root, eq.ns) for root in bad_roots)
            sol.add_step(
                action=(
                    f'Проверим, являются ли найденные корни корнями знаменателя ${sol.eq.lcm_denom_s}$. '
                    f'Корни, являющиеся корнями знаменателя, нужно выбросить.'
                ),
                solution=(
                    f'Нули знаменателя и не входит в область определения функции. Их нужно выбросить. '
                    f'Числа ${bad_roots_s}$ являются корнями знаменателя ${sol.eq.lcm_denom_s}$.'
                ),
                answer=f'Числа ${bad_roots_s}$ являются корнями знаменателя ${sol.eq.lcm_denom_s}$.',
            )
            sol.sol_codes.append('eq-quadr-remove-denom-roots')
