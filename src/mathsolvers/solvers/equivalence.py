import re
import enum
import signal
import sympy

from mathsolvers.sympy_stuff import utils, any_text_parser, ru_numers_parser
from mathsolvers.solvers_stuff import units_quantities

_expand_parms = dict(
    mul=True, multinomial=True, power_exp=True, power_base=True, force=True, log=True, complex=False, trig=True
)

__all__ = ['check_equivalence', 'CompareVerdict', 'strict_compare_v2']

Quantity = sympy.physics.units.quantities.Quantity


def check_equivalence(expr1: str, expr2: str) -> dict:
    """check_equivalence — проверить эквивалентность двух выражений, двух уравнений или двух неравенства
    Args:
        expr1: первое выражение
        expr2: второе

    Returns:
    Словарь с ключами:
    {
       'are_equal': bool,
       'diff': разница,
       'sol1': решения первого, если это уравнение/неравенство
       'sol2': решения первого, если это уравнение/неравенство
       'error': если что-то пошло не так
    }

    """
    result = {
        'expr1': expr1,
        'expr2': expr2,
    }
    try:
        expr1ex = utils.parse(expr1)
    except Exception:
        result['error'] = f'Выражение «{expr1}» чёт не парсится'
        return result
    try:
        expr2ex = utils.parse(expr2)
    except Exception:
        result['error'] = f'Выражение «{expr2}» чёт не парсится'
        return result

    op1 = re.findall('(>=|<=|>|<|=)', expr1)
    op2 = re.findall('(>=|<=|>|<|=)', expr2)
    if len(op1) > 1:
        result['error'] = f'В выражении «{expr1}» больше одного оператора: {op1}'
        return result
    if len(op2) > 1:
        result['error'] = f'В выражении «{expr2}» больше одного оператора: {op2}'
        return result
    if len(op1) != len(op2):
        result['error'] = 'Нельзя сравнивать эквивалентность выражения и уравнения/неравенства'
        return result
    if len(op1) == 0:
        diff = (expr1ex - expr2ex).simplify().expand(**_expand_parms).simplify()
        result['diff'] = utils.lat(diff)
        result['are_equal'] = diff == 0 or result['diff'] == '0'
    else:
        vars = sorted((expr1ex.free_symbols | expr2ex.free_symbols), key=lambda v: v.name)
        x = vars and vars[-1] or utils.parse('x')
        try:
            if op1[0] == '=':
                sol1 = sympy.solveset(expr1ex, x, domain=sympy.S.Reals)
            else:
                sol1 = sympy.solve_univariate_inequality(expr1ex, x, relational=False, domain=sympy.S.Reals)
        except Exception:
            result['error'] = f'«{expr1}» что-то не решается...'
            return result
        try:
            if op2[0] == '=':
                sol2 = sympy.solveset(expr2ex, x, domain=sympy.S.Reals)
            else:
                sol2 = sympy.solve_univariate_inequality(expr2ex, x, relational=False, domain=sympy.S.Reals)
        except Exception:
            result['error'] = f'«{expr2}» что-то не решается...'
            return result
        result['are_equal'] = sol1 == sol2
        result['sol1'] = str(sol1)
        result['sol2'] = str(sol2)
    return result


re_div = re.compile(r'\\(?:div|colon)(?:\b|(?=\d))|[÷:∶➗]')
re_underscore_one = re.compile(r'_1(?!\d)')
re_common_words = re.compile(
    r'\b(?:(?:я\s+)?поняла?[!.]*|(?:я\s+)?перепутала?[!.]*|ответ|примерно|ой|это|будет|ну|точно|^\s*в (?=\d)|так|думаю|цел(?:ых)?(?: и)?|а[а-]{1,}а)\b[:,!]?')
re_emoji_pattern = re.compile(
    "["
    "\U0001F300-\U0001F5FF"  # Символы Misc Symbols and Pictographs
    "\U0001F600-\U0001F64F"  # Эмодзи для смайлов
    "\U0001F680-\U0001F6FF"  # Транспортные и прочие символы
    "\U0001F700-\U0001F77F"  # Алхимические символы (иногда попадаются)
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"  # Дополнительные эмодзи (лица, жесты)
    "\U0001FA00-\U0001FAFF"  # Другие новые эмодзи
    "\U00002702-\U000027B0"  # Некоторые символы-«звёздочки» и т.п.
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE
)
re_numerical = re.compile(r'(?:-|(?<=\d))(?:й|ой|ий|ый)\b', flags=re.IGNORECASE)  # 3-й 5ый
re_degrees = re.compile(r'\^?\s*(?:°|\\circ)\s*(?:[cс]|\\text\{[cс]})?', flags=re.IGNORECASE)  # $6^\circ \text{C}$
re_root = re.compile(r'кор(?:ень|ней|ня)\s*(?:из\s*)?')  #
re_spaces_in_numbers = re.compile(r'(?<=\d)[.,，] (?=\d)')
re_power_fixer = re.compile(r'\s*во?\s*(?:степени)?\s*(\S+)\s*(?:степени)?', flags=re.IGNORECASE)  # 0,8 в степени 15; 9 в степени 33
re_word_frac = re.compile(r'^(\d+(?:[.,]\d+)?)\s+к\s+(\d+(?:[.,]\d+)?)$')


def _prepare_expr(expr: str) -> str:
    # Обрезаем пробелы
    expr = expr.strip()
    expr = expr.replace('$', '')
    # удаляем возможно окружающие формулу latex-скобки
    if (expr.startswith('\\(') and expr.endswith('\\)')) or (expr.startswith('\\[') and expr.endswith('\\]')):
        expr = expr[2:-2]
    expr = expr.lower()
    expr = expr.replace(';', ' ')  # Оно парсится странно
    expr = expr.replace('\n', ' ')
    expr = re_underscore_one.sub('', expr)
    expr = re_div.sub(r'/', expr)
    expr = expr.replace('≈', '=').replace('\\approx', '=')
    # заменяем корни
    expr = re_root.sub('√', expr)
    # Степени, указанные явно
    if 'степени' in expr:
        expr = re_power_fixer.sub(r'^{\1}', expr)
    # Убираем пробелы в числах. Типа 4, 2 вместо 4.2
    expr = expr.replace('，', ',')
    expr = re_spaces_in_numbers.sub('.', expr)
    # удаляем частотные незначащие слова и эмодзи
    expr = re_common_words.sub('', expr)
    expr = re_emoji_pattern.sub('', expr)
    expr = re_numerical.sub('', expr)
    # Заменяем текстовые варианты записать числа
    expr = ru_numers_parser.replace_ru_numbers(expr)
    # Убираем градусы
    expr = re_degrees.sub('', expr)
    # Разнообразные скорости
    expr = expr.replace('в час', '/ч').replace('в минуту', '/мин').replace('в секунду', '/с')
    # Греческие буквы частотные
    expr = expr.replace('α', 'a').replace('\\alpha', 'a')
    expr = expr.replace('θ', 't').replace('\\theta', 't')
    expr = expr.replace('ρ', 'p').replace('\\rho', 'p')
    expr = expr.replace('π', '\\pi')
    # 1 к 7
    if m := re_word_frac.fullmatch(expr):
        expr = f'{m.group(1)}/{m.group(2)}'
    return expr


# слова из 2+ букв, слово не может заканчиваться на дефис
re_ru_words = re.compile(r'[а-яА-ЯёЁ][а-яА-ЯёЁ-]+(?<!-)')
# единица измерения (не рядом с другими буквами, но может быть со степенью, типа м^2)
re_any_one_letter_unit = re.compile(
    r'(?:\b|(?<![а-яА-ЯёЁa-zA-Z]))[вглмстцч](?:\b|(?![а-яА-ЯёЁa-zA-Z]))(?:\s*(?:\*\*|\^)\s*[23]\b)?'
)
replace_ru_tbl = str.maketrans('укегхаросм', 'ykerxapocm')


def _remove_words(expr: str) -> tuple[str, int]:
    prev_len = len(expr)
    expr = re_ru_words.sub('', expr)
    expr = re_any_one_letter_unit.sub('', expr)
    # однобуквенные слова мы не вырезаем, там может быть x (хэ вместо икс) и т.п.
    expr = expr.translate(replace_ru_tbl)
    len_delta = prev_len - len(expr)
    return expr, len_delta


def strict_compare(expr1: str, expr2: str) -> bool:
    expr1 = _prepare_expr(expr1)
    expr2 = _prepare_expr(expr2)
    if expr1 == expr2:
        return True

    try:
        parsed1 = utils.parse(expr1)
        parsed2 = utils.parse(expr2)
        parsed1 = utils.normalize_terms_order_deep(parsed1)
        parsed2 = utils.normalize_terms_order_deep(parsed2)
        parsed1_s = utils.lat(parsed1)
        parsed2_s = utils.lat(parsed2)
    except Exception:
        return False
    if parsed1_s == parsed2_s:
        return True

    p1_has_vars = len(parsed1.free_symbols) > 0 or parsed1.has(Quantity)
    p2_has_vars = len(parsed2.free_symbols) > 0 or parsed2.has(Quantity)
    if p1_has_vars + p2_has_vars == 1:
        # ровно с одной стороны какие-то "единицы измерения". Тогда выкинем все русские слова
        expr1, dlen1 = _remove_words(expr1)
        expr2, dlen2 = _remove_words(expr2)
        if dlen1 + dlen2 > 20:
            # Слишком много текста
            return False
    elif p1_has_vars + p2_has_vars == 0 and expr1.count('=') + expr2.count('=') == 1:
        # Особый случай.  2 + 5 = 7  vs 7. Тогда 2+5 отрезаем
        if '=' in expr1 and parsed1.simplify() == True:  # noqa
            expr1 = expr1[expr1.index('=') + 1:]
        elif '=' in expr2 and parsed2.simplify() == True:  # noqa
            expr2 = expr2[expr2.index('=') + 1:]
    else:
        expr1 = expr1.translate(replace_ru_tbl)
        expr2 = expr2.translate(replace_ru_tbl)
    # Пробуем ещё раз, но без слов
    try:
        parsed1 = utils.parse(expr1)
        parsed2 = utils.parse(expr2)
        parsed1 = utils.normalize_terms_order_deep(parsed1)
        parsed2 = utils.normalize_terms_order_deep(parsed2)
        parsed1_s = utils.lat(parsed1)
        parsed2_s = utils.lat(parsed2)
    except Exception:
        return False
    if parsed1_s == parsed2_s:
        return True
    # Особый случай. 5 vs x = 5
    if parsed1.is_Equality and parsed1.lhs.is_Symbol and not parsed2.is_Equality and utils.lat(
            utils.normalize_terms_order_deep(parsed1.rhs)) == parsed2_s:
        return True
    elif parsed2.is_Equality and parsed2.lhs.is_Symbol and not parsed1.is_Equality and utils.lat(
            utils.normalize_terms_order_deep(parsed2.rhs)) == parsed1_s:
        return True
    # Пока ничего не сработало
    return False


class CompareVerdict(enum.IntEnum):
    NOT_EQUAL = -1
    ERROR = 0
    MAY_BE = 1
    EQUAL = 2


TOO_MANY_RUSSIAN_SYMBOLS_LIMIT = 10

prefix_trie_with_units = any_text_parser.build_trie(
    s.lower()
    for s in units_quantities.UNITS_PARSE_DICT.keys()
    if s.lower() not in {'а', 'к'}  # Скорее у нас русское а/к вместо латинской, чем ары или копейки
)
regex_pattern_with_units = any_text_parser.trie_to_regex(prefix_trie_with_units)
re_any_unit = re.compile(
    fr"""
    # Опциональный префикс "кв." с возможными пробелами
    (?:кв\.\s*)?
    # Опциональные символы деления (÷, :, ∶, ➗, /) + возможные пробелы
    (?:[÷:∶➗/]\s*|в\s+|за\s+)?
    # Начало слова (word boundary) или цифра
    (?:\b|(?<=\d))
    # Основная часть: шаблон, описывающий единицы измерения
    {regex_pattern_with_units}
    # Конец слова (word boundary) или цифра
    (?:\b|(?=\d)|[²³])
    # Опциональный блок для возведения в степень
    (?:
       (?:
           \s*
           (?:\^|\*\*)
           \s*
           \{{?\d\}}?
           (?=\b|\D)
       ) |
        # Возведение в степень юникодом
        (?:\s*[²³])
    )?
    """,
    flags=re.IGNORECASE | re.VERBOSE
)


def _reparse_expr(expr: str) -> tuple[sympy.Expr, str]:
    parsed, ns = utils.parse_and_ns(expr, rep_parenthesis=False)
    parsed = utils.normalize_terms_order_deep(parsed)
    parsed_s = utils.lat(parsed)
    return parsed, parsed_s


def _time_inserter(expr, has_hours, has_minutes, has_seconds):
    if has_hours and not has_minutes and has_seconds:
        return expr
    nums = re.findall(r'\d+', expr)
    if has_hours + has_minutes + has_seconds != len(nums):
        return expr
    use_times = []
    if has_seconds:
        use_times.append('с ')
    if has_minutes:
        use_times.append('мин ')
    if has_hours:
        use_times.append('ч ')

    def replacer(match):
        return match.group(1) + use_times.pop()

    expr.lstrip(' в')
    expr_rep = re.sub(r'(\d+)[:./]?', replacer, expr)
    return expr_rep


unit_replacer = {
    unit: sympy.Mul(scale, dst_unit)
    for unit, (scale, dst_unit) in units_quantities.UNITS_CONVERTER.items()
}
# Подхачим отдельные однобуквенные единицы измерения
unit_replacer[utils.parse('m')] = sympy.Mul(*units_quantities.UNITS_CONVERTER[units_quantities.m])
unit_replacer[utils.parse('c')] = sympy.Mul(*units_quantities.UNITS_CONVERTER[units_quantities.s])
unit_replacer[utils.parse('r')] = sympy.Mul(*units_quantities.UNITS_CONVERTER[units_quantities.g])
unit_replacer[utils.parse('pi')] = sympy.core.Integer(180)
unit_replacer[utils.parse('\\pi')] = sympy.core.Integer(180)
unit_replacer[sympy.pi] = sympy.core.Integer(180)

re_comma_not_in_number = re.compile(r'\D\s*,|,\s*\D')
re_comparison = re.compile('>=|<=|==|<|>|=')
re_has_implicit_power = re.compile(r'(?:\b|(?!<[a-zA-Zа-яёА-ЯЁ]))([a-zA-Zа-яёА-ЯЁ)])(\d+)\b')
re_implicit_division = re.compile(r'(?<=/)(?!\s*ncr\s*\()\s*((?:(?:\d+(?=\b|\D)|[a-zA-Zа-яёА-ЯЁ])(?:(?:\^|\*\*)\{?\d\}?)?){2,4})')
re_repeated_division = re.compile(r'/\s*\w+\s*/')
re_i_and_na_as_mul = re.compile(r'\b(?:и|на)\b', flags=re.IGNORECASE)
re_decimal_sep = re.compile(r'(?<=\d)(?:[,.]|\{,\})(?=\d|\(\d)|frac|/')  # 123.12, 123,12, 123{,}(12) \frac{1}{2} 3/5
re_remove_thousands_separators = re.compile(r'(?<=\d)(?<!\b0)[ ,.](?=\d{3}(?:[ ,.]\d{3})*\s*(?:[^\s\d/]|$))')  # 1,123,456  1.123.512
re_has_plus_minus = re.compile(r'\\pm|\\mp|\+\-|\-\+')


def _prepare_strict_input(expr: str) -> str:
    chunks = list(utils.ncr_chunks(expr))
    # Reject lists of answers while allowing a comma between nCr arguments.
    ordinary_commas = ''.join(' ' if kind == 'separator' else part for kind, part in chunks)
    if re_comma_not_in_number.search(ordinary_commas):
        raise ValueError('Unexpected comma in answer')
    return _prepare_expr(''.join(part for _, part in chunks))


def _remove_thousands_outside_ncr(expr: str) -> str:
    return ''.join(
        re_remove_thousands_separators.sub('', part) if kind == 'text' else part
        for kind, part in utils.ncr_chunks(expr)
    )


def _strict_compare_v2_inner(expr1: str, expr2: str) -> CompareVerdict:
    #########################
    # Откидываем то, что парсится криво
    #########################
    # Из-за особенности парсера "a < b < c" парсится криво
    if len(re_comparison.findall(expr1)) > 1 or len(re_comparison.findall(expr2)) > 1:
        return CompareVerdict.ERROR

    #########################
    # Начинаем сравнивать.
    # По очереди проверяем разные гипотезы с тем, как одинаковые ответы могут быть записаны по-разному
    #########################

    expr1_orig = expr1
    expr2_orig = expr2
    # Может быть, они просто равны?
    expr1 = _prepare_strict_input(expr1)
    expr2 = _prepare_strict_input(expr2)
    if expr1 == expr2 and not utils.ncr_call.search(expr1):
        return CompareVerdict.EQUAL

    # Так, возможно используются запятые или точки как разделители тысяч (ровно в одном из ответов)
    if (bool(re_decimal_sep.search(expr1))) + bool(re_decimal_sep.search(expr2)) == 1:
        # То есть если, условно, правильный ответ "1000", а школьник сдаёт "1.000", то из второго удаляем разделитель
        expr1 = _remove_thousands_outside_ncr(expr1)
        expr2 = _remove_thousands_outside_ncr(expr2)

    # Возможно, и там, и там есть +-. Тогда заменим его на отдельную переменную, скажем, ι
    if len(re_has_plus_minus.findall(expr1)) == len(re_has_plus_minus.findall(expr2)) > 0:
        expr1 = re_has_plus_minus.sub('+ ι*', expr1)
        expr2 = re_has_plus_minus.sub('+ ι*', expr2)

    # Ок, ну не равны. Может, просто коммутативностью воспользуемся, и всё ок? Типа 2 + 3*4 = 4*3 + 2
    parsed1, parsed1_s = _reparse_expr(expr1)
    parsed2, parsed2_s = _reparse_expr(expr2)
    if parsed1_s == parsed2_s:
        return CompareVerdict.EQUAL

    # Гипотеза: "и" или "на" используется для умножения
    expr2_fix = None
    if (expr1_fix := re_i_and_na_as_mul.sub(' * ', expr1)) != expr1 or (expr2_fix := re_i_and_na_as_mul.sub(' * ', expr2)) != expr2:
        if expr2_fix is None:
            expr2_fix = re_i_and_na_as_mul.sub(' * ', expr2)
        parsed1_fix, parsed1_s_fix = _reparse_expr(expr1_fix)
        parsed2_fix, parsed2_s_fix = _reparse_expr(expr2_fix)
        if parsed1_s_fix == parsed2_s_fix:
            return CompareVerdict.EQUAL

    # Часто ровно в одном из ответов есть единицы изменения. Тогда засчитываем без них
    p1_has_units = parsed1.has(Quantity)
    p2_has_units = parsed2.has(Quantity)
    if p1_has_units + p2_has_units == 1:
        # Если ровно с одной стороны единицы измерения, то либо это время (и требует отдельной обработки), либо просто выкинем их
        if p1_has_units:
            has_hours = parsed1.has(units_quantities.h)
            has_minutes = parsed1.has(units_quantities.mn)
            has_seconds = parsed1.has(units_quantities.s)
            if len(parsed1.free_symbols) == 0 and has_hours + has_minutes + has_seconds >= 2:
                expr2 = _time_inserter(expr2, has_hours, has_minutes, has_seconds)
                parsed2, parsed2_s = _reparse_expr(expr2)
                p2_has_units = True
            else:
                expr1 = re_any_unit.sub('', expr1)
                parsed1, parsed1_s = _reparse_expr(expr1)
        elif p2_has_units:
            has_hours = parsed2.has(units_quantities.h)
            has_minutes = parsed2.has(units_quantities.mn)
            has_seconds = parsed2.has(units_quantities.s)
            if len(parsed2.free_symbols) == 0 and has_hours + has_minutes + has_seconds >= 2:
                expr1 = _time_inserter(expr1, has_hours, has_minutes, has_seconds)
                parsed1, parsed1_s = _reparse_expr(expr1)
                p1_has_units = True
            else:
                expr2 = re_any_unit.sub('', expr2)
                parsed2, parsed2_s = _reparse_expr(expr2)

    p1_has_vars = len(parsed1.free_symbols) > 0 or p1_has_units
    p2_has_vars = len(parsed2.free_symbols) > 0 or p2_has_units
    if p1_has_vars + p2_has_vars == 1:
        # ровно с одной стороны какие-то "единицы измерения" (типа "столы"). Тогда выкинем все русские слова
        if p1_has_vars:
            expr1, dlen = _remove_words(expr1)
            parsed1, parsed1_s = _reparse_expr(expr1)
            p1_has_vars = len(parsed1.free_symbols) > 0 or parsed1.has(Quantity)
        elif p2_has_vars:
            expr2, dlen = _remove_words(expr2)
            parsed2, parsed2_s = _reparse_expr(expr2)
            p2_has_vars = len(parsed2.free_symbols) > 0 or parsed2.has(Quantity)
        if dlen > TOO_MANY_RUSSIAN_SYMBOLS_LIMIT:
            # Слишком много текста
            return CompareVerdict.ERROR

    # Особый случай.  2 + 5 = 7  vs 7. Тогда 2+5 отрезаем
    if p1_has_vars + p2_has_vars == 0 and expr1.count('=') + expr2.count('=') == 1:
        if '=' in expr1 and parsed1.simplify() == True:  # noqa: E712
            expr1 = expr1[expr1.index('=') + 1:]
        elif '=' in expr2 and parsed2.simplify() == True:  # noqa: E712
            expr2 = expr2[expr2.index('=') + 1:]
    # Особый случай. 5 vs x = 5
    elif parsed1.is_Equality and parsed1.lhs.is_Symbol and not parsed2.is_Equality:
        expr1 = expr1[expr1.index('=') + 1:]
    elif parsed2.is_Equality and parsed2.lhs.is_Symbol and not parsed1.is_Equality:
        expr2 = expr2[expr2.index('=') + 1:]
    # ещё один особый случай: x = 10 против 2 * 5 = 10
    elif parsed1.is_Equality and parsed2.is_Equality and p1_has_vars + p2_has_vars == 1:
        if (parsed1.lhs.is_Symbol and parsed2.simplify() == True) or (parsed2.lhs.is_Symbol and parsed1.simplify() == True):  # noqa: E712
            expr1 = expr1[expr1.index('=') + 1:]
            expr2 = expr2[expr2.index('=') + 1:]

    # часто пишут русские буквы вместо x, a и т.п.
    expr1 = expr1.translate(replace_ru_tbl)
    expr2 = expr2.translate(replace_ru_tbl)

    # Пробуем ещё раз, но без слов, лишних равенств и русских букв
    if parsed1_s == parsed2_s:
        return CompareVerdict.EQUAL
    parsed1, parsed1_s = _reparse_expr(expr1)
    parsed2, parsed2_s = _reparse_expr(expr2)
    if parsed1_s == parsed2_s:
        return CompareVerdict.EQUAL

    # Бывает такое, что в одном из ответов ответ в тысячах. А мы тысячи парсим. Проверим гипотезу
    if 'тыс' in expr1_orig.lower():
        if re.sub(r'(?<=\d)000\b', '', parsed1_s, count=1) == parsed2_s:
            return CompareVerdict.EQUAL
        elif parsed2 * 1000 == parsed1:
            return CompareVerdict.MAY_BE
    elif 'тыс' in expr2_orig.lower():
        if re.sub(r'(?<=\d)000\b', '', parsed2_s, count=1) == parsed1_s:
            return CompareVerdict.EQUAL
        elif parsed1 * 1000 == parsed2:
            return CompareVerdict.MAY_BE

    # 1/3x --- это (1/3)x или 1/(3x)? Пытаемся читать двояко
    if has_implicit_division := (re_implicit_division.search(expr1) or re_implicit_division.search(expr2)):
        v2_exp1 = re_implicit_division.sub(r'(\1)', expr1)
        v2_exp2 = re_implicit_division.sub(r'(\1)', expr2)
        v2_parsed1, v2_parsed1_s = _reparse_expr(v2_exp1)
        v2_parsed2, v2_parsed2_s = _reparse_expr(v2_exp2)
        if v2_parsed1_s == v2_parsed2_s:
            return CompareVerdict.EQUAL
    # x2 --- это x^2 или x*2? Пытаемся читать двояко
    if has_implicit_power := (re_has_implicit_power.search(expr1) or re_has_implicit_power.search(expr2)):
        v2_exp1 = re_has_implicit_power.sub(r'\1^(\2)', expr1)
        v2_exp2 = re_has_implicit_power.sub(r'\1^(\2)', expr2)
        v2_parsed1, v2_parsed1_s = _reparse_expr(v2_exp1)
        v2_parsed2, v2_parsed2_s = _reparse_expr(v2_exp2)
        if v2_parsed1_s == v2_parsed2_s:
            return CompareVerdict.EQUAL

    # Так, точного равенства получить не удалось.
    vars_in_expr = sorted((parsed1.free_symbols | parsed2.free_symbols), key=lambda v: v.name)
    quantities_in_expr = set(parsed1.find(lambda x: isinstance(x, Quantity))) | set(parsed2.find(lambda x: isinstance(x, Quantity)))
    # Слишком много переменных --- скорее всего какое-то слово распарсилось как произведение переменных
    if len(vars_in_expr) + len(quantities_in_expr) >= 3:
        return CompareVerdict.ERROR

    # Всё, точное равенство мы больше не обещаем, не получилось.
    # Дальше либо "точно нет", либо "может быть"
    # Поэтому заменяем все единицы измерения на универсальные эквиваленты
    parsed1 = parsed1.xreplace(unit_replacer)
    parsed2 = parsed2.xreplace(unit_replacer)

    # Здесь мы защищаемся от всех случаем неуверенности
    not_maybe_answer = CompareVerdict.NOT_EQUAL
    # if parsed1.has(Quantity) and parsed2.has(Quantity):
    #     not_maybe_answer = CompareVerdict.ERROR
    if has_implicit_division or has_implicit_power:
        not_maybe_answer = CompareVerdict.ERROR
    elif re_repeated_division.search(expr1) or re_repeated_division.search(expr2):
        not_maybe_answer = CompareVerdict.ERROR

    # Но может это точное неравенство?
    if not parsed1.is_Relational and not parsed2.is_Relational:
        diff = (parsed1 - parsed2).simplify().expand(**_expand_parms).simplify()
        if diff == 0 or utils.lat(diff) == '0' or (diff.is_Rational and diff.p == 0):
            return CompareVerdict.MAY_BE
        else:
            try:
                # Сравнение может падать при невозможности определить результат
                diff_is_small = (abs(diff) < 1e-4).simplify() == True  # noqa: E712 Тип BooleanTrue, is нельзя!
            except Exception:
                diff_is_small = False
            if diff_is_small:
                return CompareVerdict.MAY_BE
            else:
                return not_maybe_answer
    elif parsed1.is_Equality and parsed2.is_Equality:
        x = vars_in_expr and vars_in_expr[-1] or utils.parse('x')
        try:
            sol1 = sympy.solveset(parsed1, x, domain=sympy.S.Reals)
            sol2 = sympy.solveset(parsed2, x, domain=sympy.S.Reals)
            if sol1 == sol2:
                return CompareVerdict.MAY_BE
            elif len(sol1) == 1 and len(sol2) == 1:
                v1 = next(iter(sol1))
                v2 = next(iter(sol2))
                try:
                    # Сравнение может падать при невозможности определить результат
                    diff_is_small = (abs((v1 - v2).simplify()) < 1e-4).simplify() == True  # noqa: E712 Тип BooleanTrue, is нельзя!
                except Exception:
                    diff_is_small = False
                if diff_is_small:
                    return CompareVerdict.MAY_BE
                else:
                    return not_maybe_answer
        except Exception:
            return CompareVerdict.ERROR
        return not_maybe_answer
    elif parsed1.is_Relational and parsed2.is_Relational:
        x = vars_in_expr and vars_in_expr[-1] or utils.parse('x')
        try:
            sol1 = sympy.solve_univariate_inequality(parsed1, x, relational=False, domain=sympy.S.Reals)
            sol2 = sympy.solve_univariate_inequality(parsed2, x, relational=False, domain=sympy.S.Reals)
            if sol1 == sol2:
                return CompareVerdict.MAY_BE
        except Exception:
            return CompareVerdict.ERROR
        return not_maybe_answer
    else:
        return CompareVerdict.ERROR


class _TimeoutException(Exception):
    pass


def _timeout_handler(signum, frame):
    raise _TimeoutException()


signal.signal(signal.SIGALRM, _timeout_handler)


def strict_compare_v2(expr1: str, expr2: str) -> CompareVerdict:
    try:
        signal.alarm(1)
        return _strict_compare_v2_inner(expr1, expr2)
    except Exception:
        return CompareVerdict.ERROR
    finally:
        signal.alarm(0)


if __name__ == '__main__':
    # print(strict_compare_v2(*(r'140	140 машин в день'.split('\t'))))
    # print(strict_compare_v2(*(r'11м24см	11 м 24 см'.split('\t'))))
    # print(strict_compare_v2(*(r'а=R×√3	\( a = R \sqrt{3} \)'.split('\t'))))

    # print(strict_compare_v2(*('0.3 кг\t300 г'.split('\t'))))
    # print(strict_compare_v2(*(r'Ааа 12 часов	12 ч'.split('\t'))))
    # print(strict_compare_v2(*(r'12	\( 12 \mathrm{H} \)'.split('\t'))))
    # print(strict_compare_v2(*(r'Нет корней	Корней нет.'.split('\t'))))
    # print(strict_compare_v2(*(r'0，7	\(0.7\)'.split('\t'))))
    # print(strict_compare_v2(*('17 в 40 степени\t17^{40}'.split('\t'))))
    # print(strict_compare_v2(*('0,8 в степени 15\t(0.8)^{15}'.split('\t'))))
    # print(strict_compare_v2(*('а в 15\ta^{15}'.split('\t'))))
    # print(strict_compare_v2(*('45\t\\pi/4'.split('\t'))))
    # print(strict_compare_v2(*(r'6км.150м	6 км 150 м'.split('\t'))))
    # print(strict_compare_v2(*(r'2a^2-1a-8a-4	\(2a^2 + a - 8a - 4\)'.split('\t'))))
    # print(strict_compare_v2(*(r'300 гр	300 г'.split('\t'))))
    # print(strict_compare_v2(*(r'-а30	\(-a^{30}\)'.split('\t'))))
    # print(strict_compare_v2(*(r'4656	4656 тыс. руб.'.split('\t'))))
    print(strict_compare_v2(*(r'6	$6^\circ \text{C}$'.split('\t'))))
    # print(strict_compare_v2(*(r''.split('\t'))))
