import fractions
import itertools
import pprint as orig_pprint
import re

import sympy
from sympy.core import parameters
from sympy.parsing import latex
from sympy.parsing import sympy_parser as P
from sympy.physics.units import quantities

from mathsolvers.solvers_stuff import units_quantities

# Патчи
# Доп.фичи
from mathsolvers.sympy_stuff import (
    parse_fractions,
    patched_power,
    patched_sympy_parser,
    patched_transformations,
)
from mathsolvers.sympy_stuff.patched_parenthesis import Pr
from mathsolvers.sympy_stuff.patched_div import PDiv
from mathsolvers.sympy_stuff.patched_mul import IMul
from mathsolvers.sympy_stuff.patched_printers import (
    NUM_STYLE, LatexPrinterPatched, StrPrinterPatched, get_num_style
)
from mathsolvers.sympy_stuff.patched_rational import (
    DRational, FRational, MRational, PRational
)

__all__ = [
    'parse',
    'get_num_style',
    'NUM_STYLE',
    'hum',
    'lat',
    'pparse',
    'lparse',
    'pprint',
    'is_latex',
    'has_significant_change',
    'prepare_eq',
    'find_global_denominator',
    'MRational',
    'DRational',
    'FRational',
    'PRational',
]

# Нужен какой-нибудь треш, чтобы форматтеры не оптимизировали этот импорт
assert patched_power
assert patched_sympy_parser

TRANSFORMATIONS = (
    patched_transformations.mixed_fractions,
    patched_transformations.parse_abs,
    P.auto_symbol,
    patched_transformations.repeated_decimals,
    patched_transformations.auto_number,
    patched_transformations.factorial_notation,
    P.implicit_multiplication_application,
    P.implicit_application,
    P.implicit_multiplication,
    P.function_exponentiation,
    P.convert_xor,
    P.convert_equals_signs,
    patched_transformations.make_vars_real,
)
EVALUATE_FALSE = {'evaluate': False}

# процент
pcnt = sympy.Symbol('pcnt')

PARSE_LOCAL_DICT = {
    'FRational': FRational,
    'MRational': MRational,
    'DRational': DRational,
    'PRational': PRational,
    'EVALUATE_FALSE': EVALUATE_FALSE,
    # единицы измерения
    **units_quantities.UNITS_PARSE_DICT,
    'pcnt': pcnt,
    'Pr': Pr,
    'PDiv': PDiv,
    'IMul': IMul,
}

_muls = dict.fromkeys('×·∗∙⋅•⨉⨯✕⊗⊙⚫', '*')
_fracs = dict.fromkeys('/∕⁄∕⫽╱', '/')
_minuses = dict.fromkeys('−‐‑‒–—﹣－⁻₋', '-')
_pluses = dict.fromkeys('+﹢＋⁺₊', '+')
_divs = dict.fromkeys('÷:∶➗', '//')
# Мы используем хак и заменяем такое деление на //. Потом на этапе парсинга заменим его на PDiv
_divs_re = re.compile(r'\\(?:div|colon)(?:\b|(?=\d))')

_unicode_fractions = {
    '¼': ' 1/4 ', '½': ' 1/2 ', '¾': ' 3/4 ', '⅐': ' 1/7 ', '⅑': ' 1/9 ', '⅒': ' 1/10 ', '⅓': ' 1/3 ',
    '⅔': ' 2/3 ', '⅕': ' 1/5 ', '⅖': ' 2/5 ', '⅗': ' 3/5 ', '⅘': ' 4/5 ', '⅙': ' 1/6 ', '⅚': ' 5/6 ',
    '⅛': ' 1/8 ', '⅜': ' 3/8 ', '⅝': ' 5/8 ', '⅞': ' 7/8 ', '↉': ' 0/3 ',
}
_strange_unicodes = {
    '∣': '|',
}
_op_trans_table = str.maketrans(
    _muls | _fracs | _minuses | _pluses | _divs | _unicode_fractions | _strange_unicodes
)

human_printer = StrPrinterPatched({'order': 'none'})
latex_printer = LatexPrinterPatched({'order': 'none'})
human_printer._settings['symbol_names'] = {pcnt: '\\%'}
latex_printer._settings['symbol_names'] = {pcnt: '\\%'}

latex_re = re.compile(r'\\\w+|\{|\[')
unwanted_latex_to_be_removed = re.compile(r'(?:\\\\|\\|/)(?:,|[Bb]ig+[lr]|left|right|text|mathrm|begin|end)')
num_separator = re.compile(r'(?<=\d) (?=\d)')
latex_mult_re = re.compile(r'(?:\\\\|\\|/)(?:cdot|times)(?:\b|(?=\d))')
latex_div_re = re.compile(r'(?:\\\\|\\|/)(?:div)\b')
latex_frac_re = re.compile(r'(?:\\\\|\\|/)(?:slash|over)(?:\b|(?=\d))')
remove_spaces_in_nums_re = re.compile(r'(?<=\d) (?=\d{3}(?: \d{3})*\s*(?:[^\s\d/]|$))')
comma_decimal_sep_re = re.compile(r'(?<=\d)(?:,|\{,\})(?=\d|\(\d)')
le_re = re.compile(r'(?:\\\\|\\|/)leq?(?:slant)?(?:\b|(?=\d))')
ge_re = re.compile(r'(?:\\\\|\\|/)geq?(?:slant)?(?:\b|(?=\d))')
lt_re = re.compile(r'(?:\\\\|\\|/)lt(?:\b|(?=\d))')
gt_re = re.compile(r'(?:\\\\|\\|/)gt(?:\b|(?=\d))')
abs_re = re.compile(r'\|\s*([0-9a-zA-Z])\s*\|')
units_powers_with_lost_power_re = re.compile(r'\b((?:мк|[нмсдк]|)м)([23])')
fix_frac_slashed_re = re.compile(r'(?:\\\\|\\|/|(?<=[^a-zA-Zа-яА-ЯёЁ]))[cdtsx]?frac')
leading_zeros_re = re.compile(r'(?<![\d,.])0+(?=[1-9])')
latex_space_re = re.compile(r'(?<!\\)\\ ')


def is_latex(expr: str) -> bool:
    return bool(latex_re.search(expr))


def set_real_assumptions(expr: sympy.Expr, *, known_symbols={}) -> sympy.Expr:
    """В распарсенном sympy-выражении делаем переменные действительными"""
    if expr.is_Atom and expr.free_symbols:
        if expr.name not in known_symbols:
            known_symbols[expr.name] = sympy.Symbol(expr.name, real=True)
        return known_symbols[expr.name]
    if expr.args:
        new_args = [set_real_assumptions(arg) for arg in expr.args]
        return expr.func(*new_args, evaluate=False)
    return expr


def move_minuses_to_numbers(expr: sympy.Expr) -> sympy.Expr:
    if expr.is_Atom:
        return expr
    if expr.is_Mul and len(expr.args) == 2 and expr.args[0] == sympy.core.S.NegativeOne and expr.args[1].is_Rational:
        return -expr.args[1]
    if expr.args:
        return expr.func(*(move_minuses_to_numbers(arg) for arg in expr.args), evaluate=False)
    return expr


unicode_root_re = re.compile(r'√(\d+|[a-zA-Z]\b)')
unicode_root2_re = re.compile(r'√(\([^)\n]*\))')
unicode_powers_tbl = str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹', '0123456789')
unicode_powers_re = re.compile(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]+')


def unicode_power_replacer(match):
    num = match.group().translate(unicode_powers_tbl)
    return f'**{num} '


# 2/ab, 2/3ab, 2/a^3b^3, 2/7^{5}b^{4}
# implicit_division_re.findall('2/ab 2/sin 2/363 2/234a 2/2^3ab 2/a^2b^3c')
# Out[14]: ['ab', '234a', '2^3ab', 'a^2b^3c']
not_function_re = r'(?<!im|ln|re|tg)(?<!a(?:bs|rg)|c(?:os|tg)|exp|log|sin|tan)(?<!a(?:c(?:o(?:s|t)|sc)|s(?:ec|in)|tan)|cbrt|s(?:ign|qrt))\b'
implicit_division_re = re.compile(r'(?<=/)\s*((?:(?:\d+(?=\b|\D)|[a-zA-Z])(?:(?:\^|\*\*)\{\d\})?){2,4})' + not_function_re)


def pre_parse(expr: str) -> str:
    expr = expr.translate(_op_trans_table)
    expr = expr.strip(' \t\n?:.,=;$')
    # Мы используем хак и заменяем такое деление на //. Потом на этапе парсинга заменим его на PDiv
    expr = _divs_re.sub(r'//', expr)
    # Удалять пробелы из чисел 3 456 -> 3456 можно только там, где не используются единицы измерения.
    # 2^3 430см³ = 2³⁴³⁰ см³
    # м^3 430см³ = м³ + 430см³
    if not units_quantities.re_any_unit.search(expr):
        expr = remove_spaces_in_nums_re.sub('', expr)
    expr = expr.replace('$', ' ')
    expr = num_separator.sub('', expr)
    expr = latex_mult_re.sub('*', expr)
    expr = latex_div_re.sub('/', expr)
    expr = latex_frac_re.sub('/', expr)
    expr = unwanted_latex_to_be_removed.sub(' ', expr)
    expr = fix_frac_slashed_re.sub(r'\\frac', expr)
    expr = comma_decimal_sep_re.sub('.', expr)
    expr = le_re.sub(' <= ', expr)
    expr = ge_re.sub(' >= ', expr)
    expr = lt_re.sub(' < ', expr)
    expr = gt_re.sub(' > ', expr)
    expr = latex_space_re.sub(' ', expr)
    expr = leading_zeros_re.sub('', expr)  # 00123
    expr = unicode_root_re.sub(r' sqrt(\1) ', expr)  # √123, √a
    expr = unicode_root2_re.sub(r' sqrt\1 ', expr)  # √(123), √(2a)
    expr = unicode_powers_re.sub(unicode_power_replacer, expr)  # 2⁷
    expr = units_powers_with_lost_power_re.sub(r'\1^\2', expr)  # см3 -> см^3
    expr = implicit_division_re.sub(r'(\1)', expr)  # 2/36xy -> 2/(36xy)
    return expr


def parse(expr: str, *, transformations=TRANSFORMATIONS) -> sympy.Expr:
    """Parse string with math or LaTeX to sympy with real variables
    :param expr: string expression: '1 + 3x' or '\frac{1}{3} * x'
    :return: sympy expression
    """
    return parse_and_ns(expr)[0]


def parse_and_ns(expr: str, *, transformations=TRANSFORMATIONS, rep_parenthesis=True):
    saved_expr = expr = pre_parse(expr)
    ns = get_num_style(expr)
    if rep_parenthesis:
        expr = non_func_parenthesis_re.sub(' Pr(', expr)
    expr = parse_fractions.convert_fractions(expr)
    expr = expr.replace('\\sqrt', 'sqrt').replace('{', '(').replace('}', ')')
    expr = expr.replace('\\%', '%')
    expr = abs_re.sub(r'Abs(\1)', expr)
    if latex_re.search(expr):
        # print(f'oh, no, latex. {expr=} {saved_expr=}')
        parsed_expr = latex.parse_latex(saved_expr)  # parse_latex_lark
        parsed_expr = set_real_assumptions(parsed_expr)
    else:
        parameters.global_parameters.evaluate = False
        # Мы используем лютый хак для парсинга.
        # Напомним приоритеты операций:
        #   **
        #   унарные +x, -x, ~x
        #   *, @, /, //, %
        #   +, -
        #   <<, >>
        # Мы заменим
        parsed_expr = sympy.parse_expr(expr, transformations=transformations, evaluate=0, local_dict=PARSE_LOCAL_DICT)
        parameters.global_parameters.evaluate = True
    parsed_expr = move_minuses_to_numbers(parsed_expr)
    # Если среди переменных есть и заглавные, и маленькие, то заменяем большие на маленькие
    var_replacer = {
        v_upper: v_lower
        for v_upper in parsed_expr.free_symbols if v_upper.name.isupper()
        for v_lower in parsed_expr.free_symbols if v_lower.name.islower()
        if v_lower.name.upper() == v_upper.name
    }
    if var_replacer:
        parsed_expr = make_subs(parsed_expr, var_replacer)
    return parsed_expr, ns


zeros_regex = re.compile(r'(,\d*?)0+(?!\()\b')
# comma_dummy = re.compile(r'(?<=\d),(?=\D|$)')
one_dummy = re.compile(r'\b1\*')
float_re = re.compile(r'\b\d+\{?[.,]\}?\d+(?:e[-+]?\d+)?\b|\b\d+e[-+]?\d+\b')
# Обычно превращаем (...) в Pr(...), чтобы скобки сохранились.
# Но не превращаем: sin(2); 0,(3); 0.(3); 0.1(3); 2**(3); 2^(3); 1/(3) и т.п.
non_func_parenthesis_re = re.compile(
    r'(?<!in|os|tg|ln|lg|rt|xp|in|bs|\*\*|.\^|.\d|.\.|.\,|.\/|\/ )(?<!in |os |tg |ln |lg |rt |xp |in |bs |\*\* |.\^ )\('
)


def is_repeating_fraction(fr):
    denominator = fr.denominator
    while denominator % 2 == 0:
        denominator //= 2
    while denominator % 5 == 0:
        denominator //= 5
    return denominator != 1


FLOAT_ROUND = 8
FRAC_EPS = 1e-7


def float_fixer(match):
    fl = float(match.group(0).replace('{,}', '.').replace(',', '.'))
    # Может быть, это в точности дробь со знаменателем не степенью десятки?
    fr = fractions.Fraction(fl).limit_denominator(10000)
    if abs(fl - fr) < FRAC_EPS and is_repeating_fraction(fr):
        return str(fr)
    fl = round(fl, FLOAT_ROUND)
    if fl.is_integer():
        fl = int(fl)
    res = str(fl)
    if 'e' in res:
        res = f'{fl:.15f}'.rstrip('0').rstrip('.')
    return res


# def fraction_fixer(match):
#     s = match.group(0)
#     fr = fractions.Fraction(s)
#     if fr.denominator == 1:
#         return str(fr.numerator)
#     if is_repeating_fraction(fr):
#         return s
#     return str(decimal.Decimal(fr.numerator) / decimal.Decimal(fr.denominator))


fraction_re = re.compile(r'\b\d+\/\d+\b')


def normalize_terms_order(expr):
    if expr.is_Add:
        return sympy.Add(*expr.as_ordered_terms(), evaluate=False)
    if expr.is_Mul:
        args = sorted(expr.args, key=lambda expr: expr.sort_key(order=None))
        return sympy.Mul(*args, evaluate=False)
    return expr


def normalize_terms_order_deep(expr: sympy.Expr):
    if expr.is_Atom:
        return expr
    if expr.is_Add:
        return sympy.Add(*map(normalize_terms_order_deep, expr.as_ordered_terms()), evaluate=False)
    if expr.is_Mul:
        args = sorted(map(normalize_terms_order_deep, expr.args), key=lambda expr: lat(expr))
        return sympy.Mul(*args, evaluate=False)
    return expr.func(*map(normalize_terms_order_deep, expr.args), evaluate=False)


dummy_two = sympy.core.Rational(2, 1, 1)


def normalize_add_order_hacked(expr):
    if expr.args:
        # Убираем сохраняющиеся скобки
        args = [arg.args[0] if arg.func.__name__ == 'Pr' else arg for arg in expr.args]
        expr = expr.func(*args, evaluate=False)
    if expr.is_Add:
        args = expr.as_ordered_terms()
        return sympy.Add(*(normalize_add_order_hacked(arg) for arg in args), evaluate=False)
    if expr.is_Mul:
        args = expr.as_ordered_factors()
        # for i, el in enumerate(args):
        #     if el in {1, -1}:
        #         args[i] = dummy_two
        return sympy.Mul(*(normalize_add_order_hacked(arg) for arg in args), evaluate=False)
    if expr.args and expr.func:
        return expr.func(*(normalize_add_order_hacked(arg) for arg in expr.args), evaluate=False)
    return expr


def has_significant_change(expr1: sympy.Expr, expr2: sympy.Expr, ns: NUM_STYLE) -> bool:
    # if expr1.func and expr2.func:
    #     if expr1.func != expr2.func:
    #         return True
    #     if expr1.is_Add:
    #         args1 = expr1.as_ordered_terms()
    #         args2 = expr2.as_ordered_terms()
    #     elif expr1.is_Mul:
    #         args1 = expr1.as_ordered_factors()
    #         args2 = expr2.as_ordered_factors()
    #     else:
    #         args1 = expr1.args
    #         args2 = expr1.args
    #     return (
    #         len(args1) != len(args2)
    #         or any(has_significant_change(arg1, arg2) for (arg1, arg2) in zip(args1, args2))
    #     )
    # else:
    #     return expr1 != expr2
    ex1 = pm_ignore_re.sub('', lat(normalize_add_order_hacked(expr1), ns))
    ex2 = pm_ignore_re.sub('', lat(normalize_add_order_hacked(expr2), ns))
    return ex1 != ex2


pm_ignore_re = re.compile(r'[\- ()]|\s*\\cdot\s*')


def has_significant_change_ignore_pm(expr1: sympy.Expr, expr2: sympy.Expr, ns: NUM_STYLE) -> bool:
    ex1 = pm_ignore_re.sub('', lat(normalize_terms_order(expr1), ns))
    ex2 = pm_ignore_re.sub('', lat(normalize_terms_order(expr2), ns))
    return ex1 != ex2


def print_fixes(expr_s: str, comma: str) -> str:
    # expr_s = float_re.sub(float_fixer, expr_s)
    expr_s = expr_s.replace('.', comma)
    expr_s = zeros_regex.sub(r'\1COMMA_DUMMY', expr_s)
    # expr_s = comma_dummy.sub(r'', expr_s)
    expr_s = expr_s.replace(',COMMA_DUMMY', '').replace('COMMA_DUMMY', '')
    expr_s = one_dummy.sub(r'', expr_s)
    return expr_s.strip()


power_regex = re.compile(r'\*\*(\d+)')
power_table = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
mul_regex = re.compile(r'(?<!\*)\*(?!\*)')


def power_printer(match):
    return match.group(1).translate(power_table)


def hum(expr: sympy.Expr, num_style=NUM_STYLE.FRAC, comma=',') -> str:
    """Convert sympy expression to human-readable string
    :param expr: sympy expression
    :param comma: whether to replace dot to comma in numbers (7.5 -> 7,5)
    :return: Human readable string
    """
    # expr_s = printing.sstr(expr, order='none')  #
    human_printer.set_num_style(num_style)
    expr_s = human_printer.doprint(expr)
    expr_s = print_fixes(expr_s, comma)
    expr_s = power_regex.sub(power_printer, expr_s)
    expr_s = expr_s.replace('-', '−')
    expr_s = mul_regex.sub('·', expr_s)
    expr_s = expr_s.replace('sqrt', '√')
    return expr_s


def lat(expr: sympy.Expr, num_style=NUM_STYLE.FRAC, comma=',') -> str:
    """Convert sympy expression to latex string
    :param expr: sympy expression
    :param comma: whether to replace dot to comma in numbers (7.5 -> 7,5)
    :return: LaTeX string
    """
    latex_printer.set_num_style(num_style)
    expr_s = latex_printer.doprint(expr)
    expr_s = print_fixes(expr_s, comma)
    expr_s = expr_s.replace('\\left', '').replace('\\right', '')
    return expr_s


def prepare_eq(expr: str) -> tuple[dict, sympy.Expr | None, sympy.Expr | None, set | None]:
    result = {
        'task': expr,
    }
    parts = expr.split('=')
    if len(parts) != 2:
        result['error'] = f'В выражении «{expr}» должен быть ровно один символ равенства «=»'
        return result, None, None, None
    left, right = parts
    try:
        left = parse(left)
    except Exception:
        result['error'] = f'Левая часть равенства «{left}» чёт не парсится'
        return result, None, None, None
    try:
        right = parse(right)
    except Exception:
        result['error'] = f'Правая часть равенства «{right}» чёт не парсится'
        return result, None, None, None
    vars = sorted((left.free_symbols | right.free_symbols), key=lambda v: v.name)
    return result, left, right, vars


def find_global_denominator(expr: sympy.Expr, *other: sympy.Expr):
    exprs = [expr.expand().simplify()]
    exprs.extend(other_expr.expand().simplify() for other_expr in other)
    muls = []
    for i in range(10):  # some dummy limit
        denominators = [
            sympy.fraction(term)[1]
            for term in itertools.chain.from_iterable(expr.as_ordered_terms() for expr in exprs)
            if term.free_symbols
        ]
        next_lcm_denom = sympy.lcm(denominators).factor()
        if next_lcm_denom == 1:
            break
        muls.append(next_lcm_denom)
        exprs = [(expr * next_lcm_denom).expand().simplify() for expr in exprs]
    res_denom = sympy.Mul(*muls, evaluate=False)
    res_denom = normalize_terms_order(res_denom.simplify())
    if res_denom.is_Mul:
        res_denom = sympy.Mul(*(normalize_terms_order(el) for el in res_denom.args), evaluate=False)
    return res_denom


def pparse(expr: str):
    s, ns = parse_and_ns(expr)
    print(hum(s, ns))


def lparse(expr: str):
    s, ns = parse_and_ns(expr)
    print(lat(s, ns))


def split_numer_denom(expr: sympy.Expr):
    if expr.func and expr.func.__name__ == 'Pr':
        expr = expr.args[0]  # (см. mathsolvers.sympy_stuff.patched_parenthesis)
    numer, denom = [], []
    for term in sympy.Mul.make_args(expr):
        if term.func and term.func.__name__ == 'Pr':
            term = term.args[0]  # (см. mathsolvers.sympy_stuff.patched_parenthesis)
        if term.is_Pow:
            b, ex = term.args
            numer2, denom2 = split_numer_denom(b)
            if ex.is_negative:
                if ex is sympy.core.S.NegativeOne:
                    numer.extend(denom2)
                    denom.extend(numer2)
                elif ex.is_constant() and ex.is_Integer:
                    numer.extend(sympy.Pow(arg, -ex, evaluate=False) for arg in denom2 if arg != 1)
                    denom.extend(sympy.Pow(arg, -ex, evaluate=False) for arg in numer2 if arg != 1)
                else:
                    numer.append(term)
            elif ex.is_positive:
                if ex is sympy.core.S.One:
                    numer.extend(numer2)
                    denom.extend(denom2)
                elif ex.is_constant() and ex.is_Integer:
                    numer.extend(sympy.Pow(arg, ex, evaluate=False) for arg in numer2 if arg != 1)
                    denom.extend(sympy.Pow(arg, ex, evaluate=False) for arg in denom2 if arg != 1)
                else:
                    numer.append(term)
            else:
                numer.append(term)
        elif term.is_Rational and not term.is_Integer and not isinstance(term, DRational):
            if term.p != 1:
                numer.append(term.p)
            denom.append(term.q)
        elif term.is_Mul:
            numer2, denom2 = split_numer_denom(term)
            numer.extend(numer2)
            denom.extend(denom2)
        elif term != sympy.core.S.One:
            numer.append(term)
    return numer, denom


def mul_from_numer_denom(numer: list[sympy.Expr], denom: list[sympy.Expr], starts_from_negative_one=False):
    if (
            len(denom) == 1
            and (isinstance(denom[0], int) or denom[0].is_Integer)
            and any(isinstance(el, int) or el.is_Integer for el in numer)
            and sum((isinstance(el, int) or el.is_Rational) and bool(el < 0) for el in numer) <= 1
    ):
        sgn = -1 if starts_from_negative_one else 1
        for ind, el in enumerate(numer):
            if isinstance(el, int) or el.is_Integer:
                numer[ind] = sympy.Rational(el * sgn, denom[0], gcd=1)
                break
        return sympy.Mul(*numer, evaluate=False)
    sgn = [-1] if starts_from_negative_one else []
    return sympy.Mul(*sgn, *numer, *(sympy.Pow(arg, -1, evaluate=False) for arg in denom), evaluate=False)


def make_subs(expr: sympy.Expr | sympy.Basic, vals: dict[sympy.Symbol | quantities.Quantity, sympy.Expr]) -> sympy.Expr:
    if expr.is_Atom and (expr.free_symbols or isinstance(expr, quantities.Quantity)):
        return vals.get(expr, expr)
    if expr.args:
        new_args = [make_subs(arg, vals) for arg in expr.args]
        return expr.func(*new_args, evaluate=False)
    return expr


def dfs(expr, depth=0, res=None):
    root = False
    if res is None:
        res = []
        root = True
    res.append(f'{"  " * depth} {expr.func.__name__} {expr.atoms() if expr.is_Atom else expr.args}')
    for arg in expr.args:
        dfs(arg, depth + 1, res)
    if root:
        res = '\n'.join(res)
        print(res)
        return res


def srepr(expr: sympy.Expr, ev_false=False):
    if expr.is_Integer:
        return str(expr)
    if expr.is_Rational:
        return f'{expr.__class__.__name__}({expr.p}, {expr.q}, gcd=1)'
    if expr.is_Atom:
        return repr(expr)
    fname = expr.func.__name__
    args = [srepr(arg) for arg in expr.args]
    ev = ', evaluate=False' if ev_false else ''
    return f'{fname}({", ".join(args)}{ev})'


_pp = orig_pprint.PrettyPrinter(indent=2, width=120, compact=False, sort_dicts=False)


def pprint(expr):
    _pp.pprint(expr)


if __name__ == '__main__':
    print(parse(r'2м3см'))
    # складываем
    # print(parse('м см'))  # Constant followed by constant
    # print(parse('2м см'))  # Constant followed by constant
    # print(parse('2м 3см'))  # Constant followed by constant
    # print(parse('м (2 + 3)см'))  # Constant followed by parenthesis
    # print(parse('2м (2 + 3)дм'))  # Constant followed by parenthesis
    # print(parse('м sqrt(2) дм'))  # Constant followed by (implicitly applied) function
    # print(parse('sin 2 м sqrt(2) м '))  # Applied function followed by implicitly applied function
    # print(parse('sin 2 м (2м)'))  # Applied function followed by an open parenthesis
    # print(parse('sqrt(2) м (2м)'))  # Applied function followed by an open parenthesis
    # print(parse('2м 3см'))
    # print(parse('2 м**2 3 дм^{2}'))
    # print(parse('2 м^2 дм^{2}'))
    # print(parse('2 м**{2} 3 дм^{2}'))
    # print(parse('2 м^{2} 3 дм^{2}'))
    # print(parse(r'\frac{2}{3} м^{2} \frac{2}{3} дм^{2}'))
    # print(parse('2 sqrt(2) м  3 sqrt(3) см'))
    # print(parse('1 : 1 2/3'))  # TODO!
    # print(parse('x + 1'))  # TODO!
    # print(parse('2,06x - 0,6 x'))  # TODO!
    # print(parse('5 дм^3 430 см^3'))
    # print(pparse('(2+3) // (x + y)'))
    # print(pparse('(2+3) << (x + y)'))
    # print(pparse('(2+3) + 4'))
    # print(split_numer_denom(parse('(2.5 * 3/5)/(3.5 * 7/9)')))
    # print(lat(sympy.Mul(4, -2, evaluate=False)))
    # print(lat(sympy.Add(0, sympy.Mul(-1, -2, 4, evaluate=False), evaluate=False)))
    # print(lat(parse('(-6) + (1 + 2) + 3')))
    # print(lat(parse('-6 + (1+2)+3')))
    # print(lat(parse('30 : 6')))
    # print(hum(parse('30 : 6')))
    # print(lat(parse('(60/2) : 6')))
    # print(hum(parse('(60/2) : 6')))
    # print(lat(parse('30 : (12/2)')))
    # print(hum(parse('30 : (12/2)')))
    # print(lat(parse('(60/2) : (12/2)')))
    # print(hum(parse('(60/2) : (12/2)')))
    # print(lat(parse('2^{30 : 6}')))
    # print(hum(parse('2^{30 : 6}')))

    # print(lat(parse('3 (4)')))
    # print(lat(parse('(3) (4)')))
    # print(lat(parse('(3) 4')))
    # print(lat(parse('3 (-4)')))
    # print(lat(parse('(-3) (-4)')))
    # print(lat(parse('(-3) 4')))
