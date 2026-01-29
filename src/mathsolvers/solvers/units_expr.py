# flake8: noqa: E501
import re
import sympy

from mathsolvers.solvers_stuff import classes
from mathsolvers.solvers_stuff import units_quantities as uq
from mathsolvers.sympy_stuff import utils

__all__ = ['units']

Quantity = sympy.physics.units.quantities.Quantity

# это регулярка-хук для исправления вывода единиц измерения
un_joinded = '|'.join(sorted((utils.lat(u) for u in uq.UNITS_SYMBOLS), key=lambda u: (-len(str(u)), str(u))))
re_unit_without_one = re.compile(rf'(?:(?<=[$\{{\(+\-=])|^) *(?={un_joinded})')

UNITS_NS = utils.NUM_STYLE.DECIMAL | utils.NUM_STYLE.MIXED


def ulat(expr: sympy.Expr, num_style=UNITS_NS, comma=',') -> str:
    s = utils.lat(expr, num_style, comma)
    fixed_units = re_unit_without_one.sub(' 1 ', s)
    return fixed_units.strip()


def find_quantities(expr, res=None):
    if res is None:
        res = set()
    if expr.is_Atom:
        if isinstance(expr, Quantity):
            return expr
        return None
    if expr.is_Pow and isinstance(expr.args[0], Quantity) and expr.args[1].is_Rational:
        return expr
    args = []
    for arg in expr.args:
        qarg = find_quantities(arg, res)
        if qarg:
            args.append(qarg)
    if expr.is_Pow and expr.args[1].is_Rational:
        args.append(expr.args[1])
    return expr.func(*args, evaluate=False)


subs_vals = {q: u * v for (q, (u, v)) in uq.UNITS_CONVERTER.items() if q != v}


def _sort_key(expr: sympy.Expr):
    num, un = sympy.Abs(expr).as_coeff_Mul()
    scale = uq.UNITS_CONVERTER.get(un, [1, 1])[0]
    return scale


def change_units_order(expr: sympy.Expr):
    if expr.is_Add:
        args = list(expr.args)
        args.sort(key=_sort_key, reverse=True)
        return sympy.Add(*args, evaluate=False)
    return expr


def is_raw_quantity(expr: sympy.Expr) -> bool:
    return (
        isinstance(expr, Quantity)
        or expr.is_Pow
        and isinstance(expr.args[0], Quantity)
        and expr.args[1].is_Integer
        or expr.is_Mul
        and all(
            isinstance(arg, Quantity) or arg.is_Pow and isinstance(arg.args[0], Quantity) and arg.args[1].is_Integer
            for arg in expr.args
        )
    )


def _make_units_subs(expr: sympy.Expr, vals: dict[sympy.Expr, sympy.Expr]) -> sympy.Expr:
    if expr in vals:
        return vals[expr]
    if expr.args:
        new_args = [_make_units_subs(arg, vals) for arg in expr.args]
        return expr.func(*new_args, evaluate=False)
    return expr


def _remove_pm_one(expr: sympy.Expr) -> sympy.Expr:
    if expr.is_Mul:
        new_args = [_remove_pm_one(arg) for arg in expr.args]
        for ind in range(len(new_args) - 1, -1, -1):
            arg = new_args[ind]
            if arg == 1:
                new_args.pop(ind)
        if len(new_args) == 1:
            return new_args[0]
        return expr.func(*new_args, evaluate=False)
    if expr.args:
        new_args = [_remove_pm_one(arg) for arg in expr.args]
        return expr.func(*new_args, evaluate=False)
    return expr


def units(expr: str | sympy.Expr, to: list[str | sympy.Expr] = None, ns: utils.NUM_STYLE = None) -> dict:
    result = {
        'task': expr,
        'sol_codes': [],
    }

    if isinstance(expr, sympy.Expr):
        parsed = expr
        ns = ns or utils.get_num_style(utils.hum(expr))
    else:
        try:
            expr = re.sub(r'(?:\b|(?<=\d))a(?:\b|(?=\d))', 'а', expr)  # ар латиницей
            expr = re.sub(r'(?:\b|(?<=\d))c(?:\b|(?=\d))', 'с', expr)  # секунда латиницей
            expr = re.sub(r'(?:\b|(?<=\d))r(?:\b|(?=\d))', 'г', expr)  # грамм латиницей
            expr = re.sub(r'(?:\b|(?<=\d))p(?:\b|(?=\d))', 'р', expr)  # рубль латиницей
            expr = re.sub(r'(?<=[a-zA-Zа-яА-ЯёЁ]) *\.', '', expr)  # точка после единицы измерения
            parsed, ns = utils.parse_and_ns(expr)
        except Exception:
            result['error'] = f'Выражение «{expr}» чёт не парсится'
            return result
    if to is None:
        to = []
    else:
        for ind, el in enumerate(to):
            if el in uq.UNIT_TO_TYPE:
                continue
            try:
                el_parsed = utils.parse(str(el)).doit()
                assert el_parsed in uq.UNIT_TO_TYPE  # danger
                to[ind] = el_parsed
            except Exception:
                result['error'] = f'Неизвестая величина «{el}»'
                return result
    # Так, теперь parsed — sympy.Expr, выражение

    # сначала разберём несколько типичных, но простых случаев.
    # просто сумма без операций
    term_pairs = [term.doit().as_coeff_Mul() for term in parsed.as_ordered_terms()]
    is_just_sum = all(
        coeff.is_Rational and not coeff.is_negative and un in uq.UNIT_TO_TYPE for (coeff, un) in term_pairs
    )
    if is_just_sum:
        simple_res = simple_type_conversion(parsed, term_pairs, result, to)
        if 'step 1' in simple_res:
            if ',' not in simple_res['final_answer']:
                simple_res['good_scheme'] = True
            return simple_res

    # а to — List[Quantity], возможно пустой. В этом случае мы определим to по итоговому значению
    # simplefied1 = simplification.with_vars(parsed, steps, dest_ns)  # Не идеально :(
    simplified1 = parsed.simplify().expand()
    simplified1 = change_units_order(simplified1)
    # Если единицу выкинули, возвращаем её назад
    if is_raw_quantity(simplified1):
        simplified1 = sympy.Mul(1, simplified1, evaluate=False)

    parsed_s = ulat(parsed, ns)
    simplified1_s = ulat(simplified1, UNITS_NS)
    # Здесь мы получаем ответ фактически
    substed = simplified1.xreplace(subs_vals)
    simplified2 = substed.simplify().expand()
    answer_is_smallest_qu, std_un = simplified2.as_coeff_Mul()
    try:
        unit_tp = uq.UNIT_TO_TYPE[std_un]
        assert answer_is_smallest_qu.is_Number  # danger!
    except Exception:
        result['error'] = f'Не удалось определить физическую величину в выражении «{parsed_s}»'
        return result
    final_answer_is_positive = answer_is_smallest_qu >= 0
    quantities = {node for node in sympy.preorder_traversal(parsed) if isinstance(node, Quantity)}
    quantities_by_type = {}
    for qu in quantities:
        tp = uq.UNIT_TO_TYPE[qu]
        if tp not in quantities_by_type:
            quantities_by_type[tp] = []
        quantities_by_type[tp].append(qu)
    for ques in quantities_by_type.values():
        ques.sort(key=_sort_key, reverse=True)

    # Сначала упрощаем выражение
    steps: list[classes.Step] = []

    # если не упростилось, откатываем
    if sympy.count_ops(simplified1) >= sympy.count_ops(_remove_pm_one(parsed)):
        simplified1 = parsed
        simplified1_s = parsed_s

    if parsed_s != simplified1_s and utils.has_significant_change_ignore_pm(parsed, simplified1, ns):
        steps.append(
            classes.Step(
                action=f'Упростим выражение ${parsed_s}$ без преобразования единиц измерения, «приведём подобные».',
                solution=(
                    f'Упростим выражение ${parsed_s}$ без преобразования единиц измерения, «приведём подобные». '
                    f'Получится ${simplified1_s}$.'
                ),
                answer=f'${simplified1_s}$',
            )
        )
        result['sol_codes'].append('units-simplify')

    result_is_just_a_number = False
    if unit_tp == uq.UNIT_TYPE.NUMBER:
        result_is_just_a_number = True
        # все величины сократятся. Тогда мы всё, что есть, конвертируем в самую мелкую
        replaces_texts = []
        replaces_dict = {}
        for tp, ques in quantities_by_type.items():
            if len(ques) >= 1:
                # каждую из ques[:-1] преобразуем в ques[-1]
                qu_dest = ques[-1]
                dest_coef, dest_min_u = uq.UNITS_CONVERTER[qu_dest]
                for qu in ques[:-1]:
                    cur_coef, cur_min_u = uq.UNITS_CONVERTER[qu]
                    # Если единицы не соизмеримы, то увы
                    if dest_min_u != cur_min_u:
                        result['error'] = f'Нельзя преобразовать ${qu}$ в ${utils.lat(qu_dest)}$'
                        return result
                    # дроби сокращаем только 10-ки...
                    while cur_coef % 10 == 0 and dest_coef % 10 == 0:
                        cur_coef //= 10
                        dest_coef //= 10
                    coef = sympy.core.Rational(cur_coef, dest_coef, 1)
                    replaces_texts.append(
                        f'заменим везде ${ulat(qu)}$ на ${ulat(coef, UNITS_NS)} {utils.lat(qu_dest)}$'
                    )
                    replaces_dict[qu] = sympy.Mul(coef, qu_dest)
    elif unit_tp == uq.UNIT_TYPE.SPEED:
        result['error'] = 'Преобразование скорости ещё не работает'
        return result
    else:
        # Так, единицы измерения не сократились. А жаль. Это значит, что придётся выяснять,
        # какие же должны получиться в результате и использовать их.
        # Но у нас же есть фактически ответ!
        # TODO Здесь временно забиваем на возможные случаи вида '(200м + 30см) / (2 мин 20 сек)'
        terms = simplified1.as_ordered_terms()
        muls = {sympy.Abs(arg).as_coeff_Mul()[1] for arg in terms}
        if not all((bad := m) in uq.UNITS_CONVERTER for m in muls):
            result['error'] = f'Не удалось преобразовать слагаемое «{ulat(bad)}»'
            return result
        if len({uq.UNIT_TO_TYPE[m] for m in muls}) > 1:
            result['error'] = f'Среди величин «{muls}» есть такие, которые нельзя складывать'
            return result
        if not to:
            # Это — основные единицы данного типа
            to = set(uq.UNIT_TYPE_MAIN[unit_tp])
            # А ещё нужно добавить те единицы, которые были в выражении.
            # Типа 30см * 4 = 1м 20см, но 7 дм 3см + 5дм 2см = 1м 2дм 5см
            qu_in_expr = set(find_quantities(simplified1).as_ordered_terms())
            to |= qu_in_expr
            to = list(to)

        to.sort(key=_sort_key, reverse=True)
        to_coefs = [uq.UNITS_CONVERTER[t] for t in to]

        # Теперь нужно заменить каждый «плохой» mul на "хороший" из to
        replaces_texts = []
        replaces_dict = {}
        for m in muls:
            if m in to:
                continue
            orig_coef, orig_coef_u = uq.UNITS_CONVERTER[m]
            ind = 0
            while ind + 1 < len(to_coefs) and orig_coef < to_coefs[ind][0]:
                ind += 1
            dest_coef, dest_coef_u = to_coefs[ind]
            if dest_coef_u != orig_coef_u:
                result['error'] = f'Нельзя преобразовать {m} в {utils.lat(to[ind])}'
                return result

            coef = sympy.core.Rational(orig_coef, dest_coef)

            replaces_texts.append(f'заменим везде ${ulat(m)}$ на ${ulat(coef, UNITS_NS)} {utils.lat(to[ind])}$')
            replaces_dict[m] = sympy.Mul(coef, to[ind])

    if replaces_dict:
        substed2 = _make_units_subs(simplified1, replaces_dict)
        substed2_s = ulat(substed2, UNITS_NS)
        all_reps_text = ', '.join(replaces_texts)
        steps.append(
            classes.Step(
                action=f'В выражении ${simplified1_s}$ {all_reps_text}.',
                solution=(
                    f'В выражении ${simplified1_s}$ {all_reps_text}. ' f'Получится ${simplified1_s} = {substed2_s}$.'
                ),
                answer=f'${substed2_s}$',
            )
        )
        result['sol_codes'].append('units-replace')
    else:
        # никаких замен не требуется
        substed2 = simplified1
        substed2_s = simplified1_s

    simplified2 = substed2.simplify().expand()
    simplified2 = change_units_order(simplified2)
    # Если единицу выкинули, возвращаем её назад
    if is_raw_quantity(simplified2):
        simplified2 = sympy.Mul(1, simplified2, evaluate=False)

    simplified2_s = ulat(simplified2, UNITS_NS)
    if simplified2_s != substed2_s and ulat(_remove_pm_one(simplified2)) != ulat(_remove_pm_one(substed2)):
        do_simpl_text = 'Теперь упростим' if len(steps) > 0 else 'Упростим'
        steps.append(
            classes.Step(
                action=f'{do_simpl_text} полученное выражение ${substed2_s}$.',
                solution=(f'{do_simpl_text} полученное выражение ${substed2_s}$. ' f'Получится ${simplified2_s}$.'),
                answer=f'${simplified2_s}$',
            )
        )
        result['sol_codes'].append('units-simplify2')

    # Теперь при переполнении меньших слагаемых добавляем большим.
    # Сейчас у нас выражение — сумма некоторых величин из to. Должна получиться тоже сумма величин из to
    if not result_is_just_a_number:
        # to — величины
        # to_coefs — соотв. коэффициенты к базовым
        to_coefs = [pair[0] for pair in to_coefs]
        our_to_coefs = [0] * len(to)
        for term in simplified2.as_ordered_terms():
            num, qu = term.as_coeff_Mul()
            our_to_coefs[to.index(qu)] = num
        replaces_texts = []

        # некоторые числа могут быть нецелыми. Переносим остаток в меньшие разряды
        for ind in range(len(to) - 1):
            this_coeff = our_to_coefs[ind]
            if int(this_coeff) != this_coeff:
                this = our_to_coefs[ind] * to_coefs[ind]
                new_this, rem = divmod(this, to_coefs[ind])
                # rem — обязательно положительный. Разложим его
                rem_u = sympy.core.Rational(rem, to_coefs[ind])
                move = sympy.Mul(
                    rem_u, sympy.core.Rational(to_coefs[ind], to_coefs[ind + 1]), to[ind + 1], evaluate=True
                )
                if our_to_coefs[ind + 1] != 0:
                    then_add = f' И сложим ${ulat(move)}$ с ${our_to_coefs[ind + 1]} {utils.lat(to[ind + 1])}$.'
                else:
                    then_add = ''
                replaces_texts.append(
                    f'Запишем ${ulat(our_to_coefs[ind])} {utils.lat(to[ind])}$ как ${new_this} {utils.lat(to[ind])} + {ulat(move)}$.'
                    f'{then_add}'
                )
                our_to_coefs[ind] = new_this
                our_to_coefs[ind + 1] += sympy.core.Rational(rem, to_coefs[ind + 1])

        simplified3 = sympy.Add(
            *(coef * qu for (coef, qu) in zip(our_to_coefs, to, strict=False) if coef != 0), evaluate=False
        )
        simplified3_s = ulat(simplified3, UNITS_NS)
        if replaces_texts:
            all_reps_text = ' '.join(replaces_texts)
            steps.append(
                classes.Step(
                    action=all_reps_text,
                    solution=(f'{all_reps_text} ' f'Получится ${simplified2_s} = {simplified3_s}$.'),
                    answer=f'${simplified3_s}$'.replace('+', '\\ '),
                )
            )
            result['sol_codes'].append('units-change1')
        # переносим единицы измерения, которые превосходят следующий разряд (или отрицательные)
        # Тут важен знак ответа. Так как все знаки слагаемых должны быть одинаковыми.

        if not final_answer_is_positive:
            our_to_coefs = [-x for x in our_to_coefs]
            neg = sympy.Mul(-1, simplified3, evaluate=False)
            neg_s = ulat(neg)
            simplified3_rev = sympy.Add(
                *(coef * qu for (coef, qu) in zip(our_to_coefs, to, strict=False) if coef != 0), evaluate=False
            )
            simplified3_rev_s = ulat(simplified3_rev, UNITS_NS)
            steps.append(
                classes.Step(
                    action=(
                        f'Вынесем минус за скобку в выражении ${simplified3_s}$ '
                        f'чтобы дальше работать с положительной величиной.'
                    ),
                    solution=(
                        f'Вынесем минус за скобку в выражении ${simplified3_s}$. '
                        f'Получится ${neg_s} = {simplified3_rev_s}$.'
                    ),
                    answer=f'${simplified3_rev_s}$',
                )
            )
            result['sol_codes'].append('units-get-minus')
            simplified3, simplified3_s = simplified3_rev, simplified3_rev_s

        replaces_texts.clear()
        for ind in range(len(to) - 1, 0, -1):
            if our_to_coefs[ind] == 0:
                continue
            this = our_to_coefs[ind] * to_coefs[ind]
            bigger = to_coefs[ind - 1]
            add_next, rem = divmod(this, bigger)
            this_is_gt_0 = this > 0
            rem = sympy.core.Rational(rem, to_coefs[ind])
            move = sympy.Mul(add_next, sympy.core.Rational(to_coefs[ind - 1], to_coefs[ind]), to[ind], evaluate=False)
            if add_next:
                if this_is_gt_0:
                    replaces_texts.append(
                        f'Из слагаемого ${our_to_coefs[ind]} {utils.lat(to[ind])}$ вычтем ${ulat(move)}$ и перенесём в ${utils.lat(to[ind - 1])}$.'
                    )
                else:
                    if our_to_coefs[ind - 1] != 0:
                        then_add = f' И сложим ${add_next} {utils.lat(to[ind - 1])}$ с ${our_to_coefs[ind - 1]} {utils.lat(to[ind - 1])}$.'
                    else:
                        then_add = ''
                    replaces_texts.append(
                        f'Запишем ${our_to_coefs[ind]} {utils.lat(to[ind])}$ как ${add_next} {utils.lat(to[ind - 1])} + {rem} {utils.lat(to[ind])}$.'
                        f'{then_add}'
                    )
            our_to_coefs[ind] = rem
            our_to_coefs[ind - 1] += add_next
        simplified4 = sympy.Add(
            *(coef * qu for (coef, qu) in zip(our_to_coefs, to, strict=False) if coef != 0), evaluate=False
        )
        simplified4_s = ulat(simplified4, UNITS_NS)
        if replaces_texts:
            all_reps_text = ' '.join(replaces_texts)
            steps.append(
                classes.Step(
                    action=all_reps_text,
                    solution=(f'{all_reps_text} ' f'Получится ${simplified3_s} = {simplified4_s}$.'),
                    answer=f'${simplified4_s}$'.replace('+', '\\ '),
                )
            )
            result['sol_codes'].append('units-change-back')

    else:
        simplified4 = simplified2
        simplified4_s = simplified2_s

    if not final_answer_is_positive:
        neg = sympy.Mul(-1, simplified4, evaluate=False)
        neg_s = ulat(neg)
        steps.append(
            classes.Step(
                action='Вернём минус назад.', solution=f'Вернём минус назад, получится ${neg_s}$.', answer=f'${neg_s}$'
            )
        )
        simplified4, simplified4_s = neg, neg_s

    result['final_answer'] = f'${simplified4_s}$'.replace('+', '\\ ')
    if len(steps) == 0:
        parsed_s = ulat(parsed, ns)
        steps.append(
            classes.Step(
                action='Нужно ли что-то менять, чтобы преобразовать?',
                solution=f'Все числа в ${parsed_s}$ итак в нужном формате, оставим всё без изменений.',
                answer=f'${simplified4_s}$',
            )
        )

    for i, step in enumerate(steps, start=1):
        result[f'step {i}'] = step
    return result


def one_term_conversion(
    coeff: sympy.Rational, un_f: sympy.Expr, un_t: sympy.Expr, steps: list[classes.Step], already_asked_pairs: set
) -> sympy.Rational:
    if un_f == un_t:
        return coeff
    f_scale, f_sm_un = uq.UNITS_CONVERTER[un_f]
    t_scale, t_sm_un = uq.UNITS_CONVERTER[un_t]
    assert f_sm_un is t_sm_un  # TODO убрать
    # Уменьшаем или увеличиваем?
    # Пример: м -> км, маленькое в большое
    if f_scale < t_scale:
        use_f_scale = f_scale
        use_t_scale = t_scale
        use_f = un_f
        use_t = un_t
    else:
        use_f_scale = t_scale
        use_t_scale = f_scale
        use_f = un_t
        use_t = un_f

    # дроби сокращаем только 10-ки...
    # while use_f_scale % 10 == 0 and use_t_scale % 10 == 0:
    #     use_f_scale //= 10
    #     use_t_scale //= 10
    # conv_coef = sympy.core.Rational(use_t_scale, use_f_scale, 1)
    conv_coef = sympy.core.Rational(use_t_scale, use_f_scale)
    # TODO делаем промежуточные шаги для штук вида
    # - м³, км/ч и т.п., где есть степени/отношения
    # - га, л и т.п. <-> cм², км³, то есть «неестественная единица»
    if (use_t, use_f) in uq.CONVERTION_STEPS:
        conv_steps, conv_coef_muls = uq.CONVERTION_STEPS[(use_t, use_f)]
        conv_coef = sympy.Mul(*conv_coef_muls, evaluate=False)
        conv_coef_s = utils.lat(conv_coef)
        # нужно спросить про каждую пару в conv_steps, а потом сделать шаг-вердикт
        mini_verdicts = []
        for cur_f, cur_t, cur_ans in conv_steps:
            cur_ans_s = cur_ans_s2 = utils.lat(cur_ans)  # здесь обычные дроби!
            if isinstance(cur_ans, sympy.Expr):
                cur_ans = cur_ans.doit()
                cur_ans_s2 = utils.lat(cur_ans.doit())
            decl = uq.get_declension_by_number(cur_ans)
            if (cur_f, cur_t) not in already_asked_pairs:
                steps.append(
                    classes.Step(
                        action=f'Сколько {uq.DECLENSIONS[cur_t][uq.DECL.PGEN]} в {uq.DECLENSIONS[cur_f][uq.DECL.PRE]}?',
                        solution=(
                            f'В {uq.DECLENSIONS[cur_f][uq.DECL.PRE]} ${cur_ans_s}$ {uq.DECLENSIONS[cur_t][decl]}: '
                            f'${ulat(cur_f)} = {cur_ans_s2} {utils.lat(cur_t)}$.'
                        ),
                        answer=f'${cur_ans_s2}$',
                    )
                )
                already_asked_pairs.add((cur_f, cur_t))
            mini_verdicts.append(
                f'В {uq.DECLENSIONS[cur_f][uq.DECL.PRE]} ${cur_ans_s2}$ {uq.DECLENSIONS[cur_t][decl]}.'
            )
        conv_coef_fin = conv_coef.doit()
        conv_coef_fin_s = ulat(conv_coef_fin)
        mini_verdicts_s = ' '.join(mini_verdicts)
        follow_wording1 = 'Значит сколько' if mini_verdicts else 'Cколько'
        follow_wording2 = 'Значит в' if mini_verdicts else 'В'
        decl = uq.get_declension_by_number(conv_coef_fin)
        if (use_t, use_f) not in already_asked_pairs:
            steps.append(
                classes.Step(
                    action=f'{follow_wording1} {uq.DECLENSIONS[use_f][uq.DECL.PGEN]} в {uq.DECLENSIONS[use_t][uq.DECL.PRE]}?',
                    solution=(
                        f'{mini_verdicts_s} '
                        f'{follow_wording2} {uq.DECLENSIONS[use_t][uq.DECL.PRE]} ${conv_coef_s} = {conv_coef_fin_s}$ {uq.DECLENSIONS[use_f][decl]}: '
                        f'${ulat(use_t)} = {conv_coef_fin_s} {utils.lat(use_f)}$.'
                    ),
                    answer=f'${conv_coef_fin_s}$',
                )
            )
            already_asked_pairs.add((use_t, use_f))
        fin_unit_decision = f'В {uq.DECLENSIONS[use_t][uq.DECL.PRE]} ${conv_coef_fin_s}$ {uq.DECLENSIONS[use_f][decl]}.'
    else:
        conv_coef_fin = conv_coef
        conv_coef_fin_s = utils.lat(conv_coef)
        decl = uq.get_declension_by_number(conv_coef)
        if (use_t, use_f) not in already_asked_pairs:
            steps.append(
                classes.Step(
                    action=f'Сколько {uq.DECLENSIONS[use_f][uq.DECL.PGEN]} в {uq.DECLENSIONS[use_t][uq.DECL.PRE]}?',
                    solution=f'В {uq.DECLENSIONS[use_t][uq.DECL.PRE]} ${utils.lat(conv_coef)}$ {uq.DECLENSIONS[use_f][decl]}.',
                    answer=f'${utils.lat(conv_coef)}$',
                )
            )
            already_asked_pairs.add((use_t, use_f))
        fin_unit_decision = f'В {uq.DECLENSIONS[use_t][uq.DECL.PRE]} ${conv_coef_fin_s}$ {uq.DECLENSIONS[use_f][decl]}.'

    arithm_action = 'умножить'
    dest_coef = sympy.Mul(coeff, conv_coef_fin, evaluate=False)
    if f_scale < t_scale:
        dest_coef = sympy.Mul(coeff, sympy.Pow(conv_coef_fin, -1, evaluate=False), evaluate=False)
        arithm_action = 'разделить'
    dest_coef_bs = ulat(dest_coef)
    dest_coef = dest_coef.doit()
    dest_coef_as = ulat(dest_coef)
    if True:  # or coeff != 1 or f_scale < t_scale:
        dest_coef_s = ulat(dest_coef)
        impl_verdict = f'${dest_coef_bs} = {dest_coef_as}$' if dest_coef_bs != dest_coef_as else f'${dest_coef_as}$'
        steps.append(
            classes.Step(
                action=f'Переведём ${ulat(coeff)} {utils.lat(un_f)}$ в {uq.DECLENSIONS[un_t][uq.DECL.PACC]}.',
                solution=(
                    f'{fin_unit_decision} '
                    f'Значит, чтобы перевести {uq.DECLENSIONS[un_f][uq.DECL.PNOM]} '
                    f'в {uq.DECLENSIONS[un_t][uq.DECL.PACC]}, '
                    f'нужно {arithm_action} число {uq.DECLENSIONS[un_f][uq.DECL.PGEN]} на ${conv_coef_fin_s}$. '
                    f'Получим {impl_verdict}, значит получится ${dest_coef_s} {utils.lat(un_t)}$.'
                ),
                answer=f'${dest_coef_s} {utils.lat(un_t)}$',
            )
        )
    return dest_coef


def make_match_unit_addition(terms_by_unit: dict[sympy.Expr, list[sympy.Expr]], steps: list[classes.Step]):
    for un, un_terms in terms_by_unit.items():
        if len(un_terms) == 1:
            continue
        terms_back = sympy.Add(*(sympy.Mul(coeff, un) for coeff in un_terms), evaluate=False)
        terms_back_s = ulat(terms_back)
        terms_back_res = terms_back.doit()
        terms_back_res_s = ulat(terms_back_res)
        steps.append(
            classes.Step(
                action=f'Сложим {uq.DECLENSIONS[un][uq.DECL.PNOM]} c {uq.DECLENSIONS[un][uq.DECL.PINS]}: ${terms_back_s}$.',
                solution=f'Сложим ${terms_back_s}$, получится ${terms_back_res_s}$.',
                answer=f'${terms_back_res_s}$',
            )
        )
        terms_by_unit[un] = [terms_back_res.as_coeff_Mul()[0]]


def simple_type_conversion(
    expr: sympy.Expr,
    terms: list[tuple[sympy.Rational, sympy.Expr]],
    result: dict,
    to: list[sympy.Expr],
):
    steps: list[classes.Step] = []
    # Сначала вычислим итоговый ответ

    substed = expr.xreplace(subs_vals)
    calculated = substed.simplify().expand()
    res_coeff, res_unit = calculated.as_coeff_Mul()
    try:
        unit_tp = uq.UNIT_TO_TYPE[res_unit]
        assert res_coeff.is_Number  # danger!
    except Exception:
        result['error'] = f'Не удалось определить физическую величину в выражении «{ulat(expr)}»'
        return result

    # Проверим согласованность типов
    used_units = [pair[1] for pair in terms] + to
    used_types = [uq.UNIT_TO_TYPE[un] for un in used_units]
    for i in range(len(used_units) - 1):
        if used_types[i] != used_types[i + 1]:
            result['error'] = f'Единицы измерения {ulat(used_units[i])} и {ulat(used_units[i + 1])} несовместимы'
            return result

    # Так, типы согласованы. Идеально.
    # Если to не определён, то определим его
    if not to:
        # Это — основные единицы данного типа
        to = set(uq.UNIT_TYPE_MAIN[unit_tp])
        # А ещё нужно добавить те единицы, которые были в выражении.
        # Типа 30см * 4 = 1м 20см, но 7 дм 3см + 5дм 2см = 1м 2дм 5см
        qu_in_expr = set(used_units)
        to |= qu_in_expr
        to = list(to)
    to.sort(key=_sort_key, reverse=True)

    # Теперь сгруппируем все слагаемые по своим единицам изменения
    terms_by_unit: dict[sympy.Expr, list[sympy.Expr]] = {}
    for coeff, un in terms:
        if un not in terms_by_unit:
            terms_by_unit[un] = []
        terms_by_unit[un].append(coeff)
        if coeff < 0:
            all_positive = False  # noqa: F841
    has_units = sorted(terms_by_unit.keys(), key=_sort_key, reverse=True)

    # Сначала складываем всё, где больше одного слагаемого, но только если все слагаемые положительные.
    # if all(not coeff.is_negative for (coeff, un) in terms):
    make_match_unit_addition(terms_by_unit, steps)

    # Всё, теперь has_units — имеющиеся в выражении единицы измерения, упорядоченные по убыванию
    # а terms_by_unit — вычисленные коэффициенты
    # Есть два сценария решения:
    # - просто переводим каждую единицу измерения в ближайшую из to.
    # - переводим все единицы в минимальную, и считаем в ней, потом переводим обратно.
    # Первый вариант используем, если только сложения, все числа целые, и в результате не будет переполнений.
    # Второй — во всех остальных случаях: есть переполнения, отрицальные числа, или нецелые числа
    to_coefs = [uq.UNITS_CONVERTER[t] for t in to]

    dest_terms_by_unit: dict[sympy.Expr, list[sympy.Expr]] = {}
    already_asked_pairs = set()
    for un_f in has_units:
        coeff = terms_by_unit[un_f][0]
        # Теперь ищем «ближайшую» единицу измерения в to
        orig_coef, orig_coef_u = uq.UNITS_CONVERTER[un_f]
        ind = 0
        while ind + 1 < len(to_coefs) and orig_coef < to_coefs[ind][0]:
            ind += 1
        un_t = to[ind]
        dest_coeff = one_term_conversion(coeff, un_f, un_t, steps, already_asked_pairs)
        if un_t not in dest_terms_by_unit:
            dest_terms_by_unit[un_t] = []
        dest_terms_by_unit[un_t].append(dest_coeff)

    make_match_unit_addition(dest_terms_by_unit, steps)

    # Теперь нужно «прокрутить» переполнения
    for ind in range(len(to) - 1, 0, -1):
        un = to[ind]
        if un not in dest_terms_by_unit or dest_terms_by_unit[un] == 0:
            continue
        this = dest_terms_by_unit[un][0]
        bigger_un = to[ind - 1]
        over = uq.coef_second_unit_in_first(bigger_un, un)
        over_s = ulat(over)
        add_next, rem = divmod(this, over)
        if add_next:
            decl = uq.get_declension_by_number(over)
            if (bigger_un, un) not in already_asked_pairs:
                steps.append(
                    classes.Step(
                        action=f'Сколько {uq.DECLENSIONS[un][uq.DECL.PGEN]} в {uq.DECLENSIONS[bigger_un][uq.DECL.PRE]}?',
                        solution=(
                            f'В {uq.DECLENSIONS[bigger_un][uq.DECL.PRE]} ${over_s}$ {uq.DECLENSIONS[un][decl]}: '
                            f'${ulat(bigger_un)} = {over_s} {utils.lat(un)}$.'
                        ),
                        answer=f'${over_s}$',
                    )
                )
                already_asked_pairs.add((bigger_un, un))
            decl = uq.get_prepositional_declension_by_number(this)
            next_rem_ans = f'{ulat(add_next)} {utils.lat(bigger_un)} \\ {ulat(rem)} {utils.lat(un)}'
            steps.append(
                classes.Step(
                    action=(
                        f'Сколько полных {uq.DECLENSIONS[bigger_un][uq.DECL.PGEN]} в ${ulat(this)}$ {uq.DECLENSIONS[un][decl]}? '
                        f'Запишем ${ulat(this)} {utils.lat(un)}$ как полные {uq.DECLENSIONS[bigger_un][uq.DECL.PNOM]} '
                        f'и остаток {uq.DECLENSIONS[un][uq.DECL.PGEN]}.'
                    ),
                    solution=(
                        f'В {uq.DECLENSIONS[bigger_un][uq.DECL.PRE]} ${over_s}$ {uq.DECLENSIONS[un][decl]}. '
                        f'Поделим ${ulat(this)}$ на ${over_s}$ с остатком. '
                        f'Получим ${ulat(add_next)}$ (остаток ${ulat(rem)}$). '
                        f'Значит, ${ulat(this)} {utils.lat(un)} = {next_rem_ans}$.'
                    ),
                    answer=f'${next_rem_ans}$',
                )
            )
            dest_terms_by_unit[un] = [rem]
            if bigger_un not in dest_terms_by_unit:
                dest_terms_by_unit[bigger_un] = [add_next]
            else:
                # нужно сложить...
                dest_terms_by_unit[bigger_un].append(add_next)
                make_match_unit_addition(dest_terms_by_unit, steps)

    dest_terms_by_unit = {un: dest_terms_by_unit[un] for un in sorted(dest_terms_by_unit, key=_sort_key, reverse=True)}

    # Теперь ответ — это сумма слагаемых из dest_terms_by_unit
    answer_s = '\\ '.join(
        f'{ulat(coeffs[0])} {utils.lat(un)}' for (un, coeffs) in dest_terms_by_unit.items() if coeffs[0] != 0
    )
    if len(dest_terms_by_unit) > 1:
        dest_unit_text = ', '.join(
            uq.DECLENSIONS[un][uq.DECL.PACC] for (un, coeffs) in dest_terms_by_unit.items() if coeffs[0] != 0
        )
        dest_unit_text = ' и '.join(dest_unit_text.rsplit(', ', 1))
        steps.append(
            classes.Step(
                action=f'Теперь соберём вместе {dest_unit_text} и запишем ответ.',
                solution=f'Получится ${answer_s}$.',
                answer=f'${answer_s}$',
            )
        )
        result['sol_codes'].append('units-join')
    # else:
    #     steps.append(
    #         classes.Step(
    #             action=f'Теперь запишем ответ.',
    #             solution=f'Получится ${answer_s}$.',
    #             answer=f'${answer_s}$'
    #         )
    #     )
    result['sol_codes'].append('units-simple')
    for i, step in enumerate(steps, start=1):
        result[f'step {i}'] = step
    result['final_answer'] = f'${answer_s}$'
    return result


if __name__ == '__main__':
    pass
    # print(units(utils.parse('5см + 2м 312см')))
    # print(units(utils.parse('5см + 2м 312см')))
    # print(units(utils.parse('(12 м) : (1,8 км)')))
    # print(units(utils.parse('(3 дм) +  (5 см)*25')))
    # print(units(utils.parse('64 см 5 мм')))
    # print(units(utils.parse('264 м^3'), [utils.parse('дм^3')]))
    # print(units(utils.parse('5 км/ч'), [utils.parse('м/с')]))
    # print(units(utils.parse('64 см  + 64 см'), [utils.parse('м'), utils.parse('см')]))
    # print(units(utils.parse('7,65м' ), [utils.parse('м'), utils.parse('см')]))
