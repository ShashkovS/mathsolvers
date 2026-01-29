import re
from dataclasses import dataclass, asdict
import json
import warnings

import sympy
from sympy.utilities.exceptions import SymPyDeprecationWarning
# from sympy.physics import units

from mathsolvers.sympy_stuff import utils
from mathsolvers.solvers_stuff import units_quantities

__all__ = ['check_and_parse', 'AlgoparseResult']


@dataclass
class AlgoparseResult:
    expr: str
    parsed: sympy.Expr | None = None
    solver_call: str | None = None
    error: str | None = None

    dict = asdict

    def json(self) -> str:
        return json.dumps(asdict(self), default=str, ensure_ascii=False)


def build_trie(words):
    """Собираем все слова в префиксное дерево"""
    trie = {}
    for word in words:
        node = trie
        for char in word:
            node = node.setdefault(char, {})
        node['$'] = True  # End of word marker
    return trie


def trie_to_regex(node):
    """
    Собираем регулярку из префиксного дерева
    """
    if '$' in node and len(node) == 1:
        return ''
    alternatives = []
    for char, child in sorted(node.items()):
        if char == '$':
            continue
        child_regex = trie_to_regex(child)
        alternatives.append(re.escape(char) + child_regex)
    if '$' in node:
        # Конец слова
        alternatives.append('')
    if len(alternatives) == 1:
        return alternatives[0]
    else:
        # Группируем
        return '(?:' + '|'.join(alternatives) + ')'


#####################################################################
# фразочки с общими словами
task_words = [
    # глагол + что
    'найди', 'найдите', 'найти',
    'объясни', 'объясните', 'объяснить',
    'напиши', 'напишите', 'написать',
    'помоги', 'помогите', 'помочь',
    'преобразуй', 'преобразуйте', 'преобразовать',
    'посчитай', 'посчитайте', 'посчитать',
    'вычисли', 'вычислите', 'вычислить',
    'выполни', 'выполните', 'выполнить',
    'раздели', 'разделите', 'разделить',
    'раскрой', 'раскройте', 'раскрыть',
    'реши', 'решите', 'решить',
    'сложи', 'сложите', 'сложить',
    'сократи', 'сократите', 'сократить',
    'умножь', 'умножьте', 'умножить',
    'упрости', 'упростите', 'упростить',
    # что
    'задачу',
    'скобки',
    'уравнение',
    'корни',
    'дробь',
    'неравенство',
    'выражение', 'выражения', 'выражении',
    'пример',
    'многочлен',
    'умножение',
    'корень',
    'ответ',
    'значение',
    # общие фразочки
    'как', 'найти',
    'сколько', 'будет',
    'это', 'этот', 'эти', 'этим',
]
prefix_trie_with_task_words = build_trie(s.lower() for s in task_words)
regex_pattern_with_task_words = trie_to_regex(prefix_trie_with_task_words)
re_task_words = re.compile(fr'\b{regex_pattern_with_task_words}\b\s*[:?]?', flags=re.IGNORECASE)

#####################################################################
# функции и latex
parsed_func_names = [
    'Abs', 'im', 're', 'sign', 'arg', 'conjugate', 'acos', 'arccos', 'acot', 'arccot', 'acsc',
    'arccsc', 'asec', 'arcsec', 'asin', 'arcsin', 'atan', 'arctg', 'acosh', 'arccosh', 'acoth',
    'arccth', 'acsch', 'arccsch', 'asech', 'arcsech', 'asinh', 'arcsinh', 'atanh', 'arctgh', 'cos',
    'cot', 'ctg', 'csc', 'sec', 'sin', 'tan', 'tg', 'cosh', 'coth', 'cth', 'csch', 'sech', 'sinh',
    'tanh', 'th', 'exp', 'ln', 'log', 'sqrt', 'cbrt',
]
parsed_latex_commands = [
    'alpha', 'begin', 'beta', 'cdot', 'circ', 'cos', 'Delta', 'dfrac', 'div', 'dot',
    'end', 'frac', 'gamma', 'ge', 'geq', 'geqslant', 'gt', 'infty', 'le', 'left', 'leq', 'leqslant', 'lt', 'mathbb',
    'mathbf', 'mathrm', 'mathtt', 'ne', 'neq', 'pi', 'quad', 'rho', 'right', 'sin', 'sqrt', 'text',
    'textrm', 'times', 'upsilon', 'varphi', 'cases',
]

prefix_trie_with_parsed = build_trie(s.lower() for s in set(parsed_func_names + parsed_latex_commands))
regex_pattern_with_parsed = trie_to_regex(prefix_trie_with_parsed)
re_function_or_latex = re.compile(fr'(?:\b|\d|\\){regex_pattern_with_parsed}(?:\b|\d)', flags=re.IGNORECASE)

#####################################################################
# единицы измерения
prefix_trie_with_units = build_trie(s.lower() for s in units_quantities.UNITS_PARSE_DICT.keys())
regex_pattern_with_units = trie_to_regex(prefix_trie_with_units)
re_any_unit = re.compile(fr'(?:\b|\d){regex_pattern_with_units}(?:\b|\d)', flags=re.IGNORECASE)

#####################################################################
# юникод и валидные символы
parsed_unicodes = '×·∗∙⋅•⨉⨯✕⊗⊙⚫∕⁄∕⫽╱−‐‑‒–—﹣－⁻₋+﹢＋⁺₊÷:∶➗⁰¹²³⁴⁵⁶⁷⁸⁹√∣¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞↉'
latex_special_chars = r'\-+=*\\\/.<>()[\]{}|_^.,;:!?\'"!~$%&#'
letters = '0-9а-яёА-ЯЁa-zA-Z'
spaces = r'\s￼'
only_valid_symbols_re = re.compile(f'[^{parsed_unicodes}{latex_special_chars}{letters}{spaces}]')
has_words_re = re.compile(r'[а-яёА-ЯЁa-zA-Z]{3,}|[а-яёА-ЯЁ]{2,}')

#####################################################################
# разное
num_with_numeral_re = re.compile(r'\d+[\s(){}]*_[\s(){}]*\d')
text_with_and = re.compile(r'\bи\b', flags=re.IGNORECASE)
re_prob_item = re.compile(r'\A\s*№?\s*(?:\w[)№]|[а-ж]:)\s*')
re_simple_powers = re.compile(r'(?:^|(?<=[^a-zA-Zа-яА-Я]))([a-zA-Zа-яА-Я]) {,2}([2-8])(?:(?=\D)|$)')
re_bad_environments = re.compile(r'\\begin\s*\{\s*(?:cases)\s*\}')
re_empty_power = re.compile(r'\^\s*\{\s*\}')

# Преобразуем предупреждения SymPyDeprecationWarning в исключения
warnings.filterwarnings("error", category=SymPyDeprecationWarning)


def check_and_parse(expr: str) -> AlgoparseResult:
    """Проверить, что текст сразу является задачей."""

    if m := num_with_numeral_re.search(expr):
        return AlgoparseResult(
            expr=expr,
            error=f'Число с системой счисления: "{m.group()}"',
        )
    if m := text_with_and.search(expr):
        return AlgoparseResult(
            expr=expr,
            error=f'Союз "{m.group()}" в тексте',
        )
    if m := re_bad_environments.search(expr):
        return AlgoparseResult(
            expr=expr,
            error=f'Пока не парсим окружения: {m.group()}',
        )
    # Выкинем общие слова типа "реши задачу"
    cleaned = re_task_words.sub('', expr)
    cleaned = re_prob_item.sub('', cleaned)
    cleaned = re_empty_power.sub('', cleaned)
    # Сначала выкинем из текста известные нам функции, latex и единицы измерения
    without_words = re_function_or_latex.sub('', cleaned)
    without_words = re_any_unit.sub('', without_words)

    if m := has_words_re.search(without_words):
        return AlgoparseResult(
            expr=expr,
            error=f'Есть слова в выражении: "{m.group()}"',
        )

    if m := only_valid_symbols_re.search(without_words):
        return AlgoparseResult(
            expr=expr,
            error=f'Есть символы не из числа разрешённых: {m.group()}',
        )
    # Заменяем x2 на x^2 и т.п.
    cleaned = re.sub(re_simple_powers, r'\1**\2', cleaned)

    try:
        parsed, ns = utils.parse_and_ns(cleaned)
    except Exception:
        return AlgoparseResult(
            expr=expr,
            error='Не парсится',
        )
    if parsed.is_Boolean:
        return AlgoparseResult(
            expr=expr,
            error='Распарсилось в True/False',
        )
    if parsed is sympy.nan:
        return AlgoparseResult(
            expr=expr,
            error='Распарсилось в nan',
        )
    # Вах! Парсится! Что же это?
    is_Equality = parsed.is_Equality
    is_Relational = parsed.is_Relational

    if len(parsed.free_symbols) >= 3 or not is_Relational and len(parsed.free_symbols) >= 4:
        return AlgoparseResult(
            expr=expr,
            error='Слишком много переменных напарсилось',
        )
    # штуки вида y = x^2 -2x + 4 (слева символ, справа нет этого символа)
    if (
            parsed.is_Equality and parsed.lhs.is_Symbol and parsed.rhs.free_symbols and
            len(parsed.lhs.free_symbols & parsed.rhs.free_symbols) == 0
    ):
        return AlgoparseResult(
            expr=expr,
            error='На входе функция, непонятно, что с ней делать',
        )

    # has_units = parsed.has(units.Quantity)
    latex_s = utils.lat(parsed, ns)

    if is_Equality and parsed.free_symbols:
        solver = 'solve'
    elif is_Relational and parsed.free_symbols:
        solver = 'solve'
    else:
        solver = 'simplify'

    solver_call = f'<<{solver} {latex_s}>>'
    return AlgoparseResult(
        expr=expr,
        parsed=parsed,
        solver_call=solver_call,
    )


if __name__ == '__main__':
    exprs = [
        '2+2=',
        '2x+1=4',
        'найти \\frac{2}{5^2}',
        'что думаешь про 2+2',
        'Как упростить выражение: (9^6 * (-4)^5)/(-6)^10',
        '汉字 2+2',
        'xyz',
        '2м + x = 5м',
    ]
    p_cnt = 0
    e_cnt = 0
    for expr in exprs:
        res = check_and_parse(expr)
        if res.error:
            print(f'error   {expr[:60]:<62} {res.error}')
            e_cnt += 1
            # pass
        else:
            print(f'parse   {expr[:60]:<62} {res.solver_call}')
            p_cnt += 1
            # print(f'    ({expr!r}, {res["latex"]!r}, {res["solver"]!r}), ')
        # pprint.pprint(res)
    print('p_cnt=546 e_cnt=1329 <-- old')
    print(f'{p_cnt=} {e_cnt=}')
