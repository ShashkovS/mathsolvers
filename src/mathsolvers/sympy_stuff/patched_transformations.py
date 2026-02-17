# ruff: noqa: PLR2004
# PLR2004 Magic value used in comparison, consider replacing `3` with a constant variable
# ruff: noqa: N802
# N802  Function name `*` should be lowercase

from collections.abc import Callable
from fractions import Fraction
from tokenize import ERRORTOKEN, NAME, NUMBER, OP, TokenError
from typing import Any, Union

from sympy.parsing import sympy_parser
from sympy.parsing.sympy_parser import AppliedFunction, _token_callable

from mathsolvers.solvers_stuff import units_quantities

TOKEN = tuple[int, str]
DICT = dict[str, Any]
TRANS = Callable[[list[TOKEN], DICT, DICT], list[TOKEN]]


def mixed_fractions(tokens: list[TOKEN], local_dict: DICT, global_dict: DICT):
    # fix mixed fractions
    # mixed fraction "1 2/3" looks like (2, '1'), (2, '2'), (55, '/'), (2, '3') in token list
    result: list[TOKEN] = []
    tok_ind = 0
    frac_found = False
    last_frac_ind = -1
    while tok_ind < len(tokens):
        toknum, tokval = token = tokens[tok_ind]
        if toknum == OP and tokval == '/' and tok_ind > last_frac_ind + 1 and tok_ind < len(tokens) - 1:
            # Так, кажется это может быть дробью!
            toknum_p1, tokval_p1 = tokens[tok_ind - 1]
            toknum_n1, tokval_n1 = tokens[tok_ind + 1]
            # fraction
            if toknum_p1 == toknum_n1 == NUMBER and tokval_p1.isdecimal() and tokval_n1.isdecimal():
                result.pop()
                denomenator = int(tokval_n1)
                numerator = int(tokval_p1)
                # mixed
                rat = 'FRational'
                if tok_ind >= 2:
                    toknum_p2, tokval_p2 = tokens[tok_ind - 2]
                    if toknum_p2 == NUMBER and tokval_p2.isdecimal():
                        result.pop()
                        numerator += denomenator * int(tokval_p2)
                        rat = 'MRational'
                if rat == 'FRational' and result and result[-1][1] in ('^', '**'):
                    # Есть особый случай: 2^3/4 или 2**3/4 — здесь у степени приоритет выше.
                    # В этом случае забываем, что это дробь.
                    # Со смешанными дробями такого нет: 2^3 4/5 нельзя понять как (2^3) + 4/5
                    result.append((toknum_p1, tokval_p1))
                else:
                    result.append((NAME, rat))
                    result.append((OP, '('))
                    if rat == 'FRational':
                        result.append((NUMBER, str(numerator)))
                        result.append((OP, ','))
                        result.append((NUMBER, str(denomenator)))
                        result.append((OP, ','))
                        result.append((NUMBER, '1'))  # gcd — чтобы парсер не сокращал дроби
                    else:
                        result.append((NUMBER, tokval_p2))
                        result.append((OP, ','))
                        result.append((NUMBER, tokval_p1))
                        result.append((OP, ','))
                        result.append((NUMBER, tokval_n1))
                    result.append((OP, ')'))
                    frac_found = True
                    tok_ind += 1
                    last_frac_ind = tok_ind
        tok_ind += 1
        if not frac_found:
            result.append(token)
        frac_found = False
    return result


def parse_abs(tokens: list[TOKEN], local_dict: DICT, global_dict: DICT):
    result: list[TOKEN] = []
    opened_module = False
    for toknum, tokval in tokens:
        if toknum == OP and tokval == '|':
            if not opened_module:
                result.append((NAME, 'Abs'))
                result.append((OP, '('))
                opened_module = True
            else:
                # result.extend([(OP, ','), (OP, '**'), (NAME, 'EVALUATE_FALSE'), (OP, ')')])
                result.append((OP, ')'))
                opened_module = False
        else:
            result.append((toknum, tokval))
    return result


def make_vars_real(tokens: list[TOKEN], local_dict: DICT, global_dict: DICT):
    """Converts floats into ``Rational``. Run AFTER ``auto_number``."""
    result: list[TOKEN] = []
    passed_symbol = False
    for toknum, tokval in tokens:
        if toknum == NAME and tokval == 'Symbol':
            passed_symbol = True
        elif passed_symbol and toknum == OP and tokval == ')':
            result.append((OP, ','))
            result.append((NAME, 'real'))
            result.append((OP, '='))
            result.append((NAME, 'True'))
            passed_symbol = False
        result.append((toknum, tokval))
    return result


def repeated_decimals(tokens: list[TOKEN], local_dict: DICT, global_dict: DICT):
    """Allows 0.2(1) notation to represent the repeated decimal 0.2111... (19/90)

    Run this before auto_number.

    """
    result: list[TOKEN] = []

    def is_digit(s):
        return all(i in '0123456789_' for i in s)

    # num will running match any DECIMAL ( INTEGER )
    num: list[TOKEN] = []
    for toknum, tokval in tokens:
        if toknum == NUMBER:
            if (
                    not num
                    and ('.' in tokval or ',' in tokval)
                    and 'e' not in tokval.lower()
                    and 'j' not in tokval.lower()
                    or is_digit(tokval)
                    and len(num) == 2
            ):
                num.append((toknum, tokval))
            elif is_digit(tokval) and len(num) == 3 and is_digit(num[-1][1]):
                # Python 2 tokenizes 00123 as '00', '123'
                # Python 3 tokenizes 01289 as '012', '89'
                num.append((toknum, tokval))
            else:
                num = []
        elif toknum == OP:
            if tokval == '(' and len(num) == 1 or tokval == ')' and len(num) >= 3:
                num.append((OP, tokval))
            elif tokval in ('.', ',') and not num:
                # handle .(1)
                num.append((NUMBER, '0.'))
            else:
                num = []
        else:
            num = []

        result.append((toknum, tokval))

        if num and num[-1][1] == ')':
            # pre.post[repetend] = a + b/c + d/e where a = pre, b/c = post,
            # and d/e = repetend
            result = result[: -len(num)]
            pre, post = num[0][1].replace(',', '.').split('.')
            repetend = num[2][1]
            if len(num) == 5:
                repetend += num[3][1]

            pre = pre.replace('_', '')
            post = post.replace('_', '')
            repetend = repetend.replace('_', '')

            zeros = '0' * len(post)
            post, repetends = [w.lstrip('0') for w in [post, repetend]]
            # or else interpreted as octal

            a = pre or '0'
            b, c = post or '0', '1' + zeros
            d, e = repetends, ('9' * len(repetend)) + zeros
            f = int(a) + Fraction(int(b), int(c)) + Fraction(int(d), int(e))

            seq = [
                (NAME, 'PRational'),
                (OP, '('),
                (NUMBER, str(f.numerator)),
                (OP, ','),
                (NUMBER, str(f.denominator)),
                (OP, ')'),
            ]
            # seq = [
            #     (OP, '('),
            #     (NAME, 'Integer'),
            #     (OP, '('),
            #     (NUMBER, a),
            #     (OP, ')'),
            #     (OP, '+'),
            #     (NAME, 'Rational'),
            #     (OP, '('),
            #     (NUMBER, b),
            #     (OP, ','),
            #     (NUMBER, c),
            #     (OP, ')'),
            #     (OP, '+'),
            #     (NAME, 'Rational'),
            #     (OP, '('),
            #     (NUMBER, d),
            #     (OP, ','),
            #     (NUMBER, e),
            #     (OP, ')'),
            #     (OP, ')'),
            # ]
            result.extend(seq)
            num = []
    return result


def factorial_notation(tokens: list[TOKEN], local_dict: DICT, global_dict: DICT):
    """Allows standard notation for factorial."""
    result: list[TOKEN] = []
    nfactorial = 0
    for toknum, tokval in tokens:
        if toknum == OP and tokval == '!':
            # In Python 3.12 "!" are OP instead of ERRORTOKEN
            nfactorial += 1
        elif toknum == ERRORTOKEN:
            op = tokval
            if op == '!':
                nfactorial += 1
            else:
                nfactorial = 0
                result.append((OP, op))
        else:
            if nfactorial == 1:
                result = _add_factorial_tokens('factorial', result)
            elif nfactorial == 2:
                result = _add_factorial_tokens('factorial2', result)
            elif nfactorial > 2:
                raise TokenError
            nfactorial = 0
            result.append((toknum, tokval))
    return result


def _add_factorial_tokens(name: str, result: list[TOKEN]) -> list[TOKEN]:
    if result == [] or result[-1][1] == '(':
        raise TokenError()

    beginning = [(NAME, name), (OP, '(')]
    end = [(OP, ','), (OP, '**'), (NAME, 'EVALUATE_FALSE'), (OP, ')')]

    diff = 0
    length = len(result)

    for index, token in enumerate(result[::-1]):
        toknum, tokval = token
        i = length - index - 1

        if tokval == ')':
            diff += 1
        elif tokval == '(':
            diff -= 1

        if diff == 0:
            if i - 1 >= 0 and result[i - 1][0] == NAME:
                return result[: i - 1] + beginning + result[i - 1:] + end
            return result[:i] + beginning + result[i:] + end

    return result


def auto_number(tokens: list[TOKEN], local_dict: DICT, global_dict: DICT):
    """Converts numeric literals to use SymPy equivalents.

    Complex numbers use ``I``, integer literals use ``Integer``, and float
    literals use ``Float``.

    """
    result: list[TOKEN] = []

    for ind, (toknum, tokval) in enumerate(tokens):
        if toknum == NUMBER:
            number = tokval
            postfix = []

            if number.endswith('j') or number.endswith('J'):
                number = number[:-1]
                postfix = [(OP, '*'), (NAME, 'I')]

            if '.' in number or (
                    ('e' in number or 'E' in number) and not (number.startswith('0x') or number.startswith('0X'))
            ):
                f = Fraction(number)
                seq = [
                    (NAME, 'DRational'),
                    (OP, '('),
                    (NUMBER, str(f.numerator)),
                    (OP, ','),
                    (NUMBER, str(f.denominator)),
                    (OP, ','),
                    (NUMBER, '1'),  # gcd — чтобы парсер не сокращал дроби
                    (OP, ')'),
                ]
            elif (
                    ind >= 2
                    and tokens[ind - 2][1].endswith('Rational')
                    and not postfix
                    or (
                        ind >= 4
                        and tokens[ind - 1][1] == ','
                        and tokens[ind - 3][1] == '('
                        and tokens[ind - 4][1].endswith('Rational')
                        and not postfix
                    )
                    or (
                        ind >= 6
                        and tokens[ind - 1][1] == tokens[ind - 3][1] == ','
                        and tokens[ind - 5][1] == '('
                        and tokens[ind - 6][1].endswith('Rational')
                        and not postfix
                    )
            ):
                seq = [(toknum, tokval)]
            else:
                seq = [(NAME, 'Integer'), (OP, '('), (NUMBER, number), (OP, ')')]
            result.extend(seq + postfix)
        else:
            result.append((toknum, tokval))

    return result


def _implicit_multiplication_patched(tokens: list[Union[TOKEN, AppliedFunction]], local_dict: DICT, global_dict: DICT):
    """Implicitly adds '*' tokens.

    Cases:

    - Two AppliedFunctions next to each other ("sin(x)cos(x)")

    - AppliedFunction next to an open parenthesis ("sin x (cos x + 1)")

    - A close parenthesis next to an AppliedFunction ("(x+2)sin x")\

    - A close parenthesis next to an open parenthesis ("(x+2)(x+3)")

    - AppliedFunction next to an implicitly applied function ("sin(x)cos x")

    """
    result: list[Union[TOKEN, AppliedFunction]] = []
    skip = False
    for ind in range(len(tokens) - 1):
        tok = tokens[ind]
        nextTok = tokens[ind + 1]

        result.append(tok)
        if skip:
            skip = False
            continue
        if tok[0] == OP and tok[1] == '.' and nextTok[0] == NAME:
            # Dotted name. Do not do implicit multiplication
            skip = True
            continue
        if isinstance(tok, AppliedFunction):
            # 12 дм^3  6 см^3
            # 12 (дм)^3  6 (см)^3
            prev_is_unit_with_power = (
                ind >= 2
                and tokens[ind - 1][0] == OP
                and tokens[ind - 1][1] in ('**', '^')
                and (
                    (tokens[ind - 2][0] == NAME and tokens[ind - 2][1] in units_quantities.UNITS_PARSE_DICT)
                    or
                    (ind >= 3 and tokens[ind - 2][1] == ')'
                     and tokens[ind - 3][0] == NAME and tokens[ind - 3][1] in units_quantities.UNITS_PARSE_DICT)
                )
            )
            if isinstance(nextTok, AppliedFunction):
                if prev_is_unit_with_power:
                    result.append((OP, '+'))
                else:
                    result.append((OP, '@'))
            elif nextTok == (OP, '('):
                # Applied function followed by an open parenthesis
                if tok.function[1] == 'Function':
                    tok.function = (tok.function[0], 'Symbol')
                result.append((OP, '@'))
            elif nextTok[0] == NAME:
                # Applied function followed by implicitly applied function
                if prev_is_unit_with_power:
                    result.append((OP, '+'))
                else:
                    result.append((OP, '@'))
        elif tok == (OP, ')'):
            prev_is_unit_with_power = (
                ind >= 7
                and tokens[ind - 6][0] == OP
                and tokens[ind - 6][1] in ('**', '^')
                and tokens[ind - 7][0] == NAME
                and tokens[ind - 7][1] in units_quantities.UNITS_PARSE_DICT
                and tokens[ind - 5] == tokens[ind - 3] == (OP, '(')
                and tokens[ind - 4] == (NAME, 'Integer')
            )
            if isinstance(nextTok, AppliedFunction):
                # Close parenthesis followed by an applied function
                if prev_is_unit_with_power:
                    result.append((OP, '+'))
                else:
                    result.append((OP, '@'))
            elif nextTok[0] == NAME:
                # Close parenthesis followed by an implicitly applied function
                result.append((OP, '@'))
            elif nextTok == (OP, '('):
                # Close parenthesis followed by an open parenthesis
                if prev_is_unit_with_power:
                    result.append((OP, '+'))
                else:
                    result.append((OP, '@'))
        elif tok[0] == NAME and not _token_callable(tok, local_dict, global_dict):
            if (
                    # Constant followed by (implicitly applied) function
                    (
                        isinstance(nextTok, AppliedFunction)
                        or (nextTok[0] == NAME and _token_callable(nextTok, local_dict, global_dict))
                    )
                    # Constant followed by parenthesis
                    or (nextTok == (OP, '('))
                    # Constant followed by constant
                    or (nextTok[0] == NAME)
            ):
                if tok[0] == NAME and tok[1] in units_quantities.UNITS_PARSE_DICT:
                    result.append((OP, '+'))
                else:
                    result.append((OP, '@'))
    if tokens:
        result.append(tokens[-1])
    return result


sympy_parser._implicit_multiplication = _implicit_multiplication_patched
