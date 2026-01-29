# ruff: noqa: N802
# N802  Function name `*` should be lowercase

import enum
import re

import sympy

# import only for copy of patched version
from sympy.core import Expr, Mul, Rational
from sympy.core.power import Pow
from sympy.printing import StrPrinter
from sympy.printing.latex import LatexPrinter
from sympy.printing.precedence import precedence, precedence_traditional
from sympy.utilities.iterables import sift

from mathsolvers.sympy_stuff import patched_parenthesis, patched_rational

__all__ = ['NUM_STYLE', 'StrPrinterPatched', 'LatexPrinterPatched']


class NUM_STYLE(enum.IntFlag):
    FRAC = 1
    MIXED = 2
    DECIMAL = 4


NBSP = '\xa0'
NBSP_LATEX = '~'

has_decimal_re = re.compile(r'\d\{?[.,]}?\d|\d[eE][-+]?\d')
mixed_fraction_re = re.compile(r'\d+(?: +\d+\s*\/\s*\d+| *\$?\\?\\frac\{\d+\}\{\d+\})')


def get_num_style(expr: str) -> NUM_STYLE:
    num_style = NUM_STYLE.FRAC
    if mixed_fraction_re.search(expr):
        num_style |= NUM_STYLE.MIXED
    if has_decimal_re.search(expr):
        num_style |= NUM_STYLE.DECIMAL
    return num_style


def mul_to_ten_power(denominator: int):
    n2 = n5 = 0
    while denominator % 2 == 0:
        denominator //= 2
        n2 += 1
    while denominator % 5 == 0:
        denominator //= 5
        n5 += 1
    if denominator != 1:
        return None, None
    if n2 > n5:
        mul = 5 ** (n2 - n5)
    else:
        mul = 2 ** (n5 - n2)
    return mul, max(n2, n5)


def find_repeating_decimal(numerator, denominator):
    is_negative = numerator < 0
    numerator = abs(numerator)
    quotient, remainder = divmod(numerator, denominator)
    result = f'{"-" if is_negative else ""}{quotient},'
    remainders = {}
    decimal_part = ''
    position = 0
    while remainder != 0 and remainder not in remainders:
        remainders[remainder] = position
        numerator = remainder * 10
        digit, remainder = divmod(numerator, denominator)
        decimal_part += str(digit)
        position += 1
    if remainder == 0:
        final_result = result + decimal_part
    else:
        # Repeating part found
        repeat_start = remainders[remainder]
        non_repeat = decimal_part[:repeat_start]
        repeat = decimal_part[repeat_start:]
        final_result = f'{result}{non_repeat}({repeat})'
    return final_result


class StrPrinterPatched(StrPrinter):
    def set_num_style(self, style: NUM_STYLE):
        self.num_style = style

    def _print_Mul(self, expr):
        prec = precedence(expr)

        # make sure the
        # identities are visible, multiple Rational factors are not combined
        # etc so we display in a straight-forward form that fully preserves all
        # args and their order.
        args = expr.args
        d, n = sift(args, lambda x: isinstance(x, Pow) and bool(x.exp.as_coeff_Mul()[0] < 0), binary=True)
        for i, di in enumerate(d):
            if di.exp.is_Number:
                e = -di.exp
            else:
                dargs = list(di.exp.args)
                dargs[0] = -dargs[0]
                e = Mul._from_args(dargs)
            d[i] = Pow(di.base, e, evaluate=False) if e - 1 else di.base

        pre = []
        # don't parenthesize first factor if negative
        if n and not n[0].is_Add and n[0].could_extract_minus_sign():
            pre = [self._print(n.pop(0))]

        nfactors = pre + [self.parenthesize(a, prec, strict=False) for a in n]
        if not nfactors:
            nfactors = ['1']

        # don't parenthesize first of denominator unless singleton
        if len(d) > 1 and d[0].could_extract_minus_sign():
            pre = [self._print(d.pop(0))]
        else:
            pre = []
        dfactors = pre + [self.parenthesize(a, prec, strict=False) for a in d]

        n = '*'.join(nfactors)
        d = '*'.join(dfactors)
        if len(dfactors) > 1:
            return '%s/(%s)' % (n, d)
        if dfactors:
            return '%s/%s' % (n, d)
        return n

    def _print_Rational(self, expr: Rational):
        if expr.q == 1:
            return str(expr.p)
        if isinstance(expr, patched_rational.DRational):
            style = NUM_STYLE.DECIMAL
        elif isinstance(expr, patched_rational.MRational):
            return f'{expr.wp}{NBSP}{expr.np}/{expr.q}'
        elif isinstance(expr, patched_rational.FRational):
            style = NUM_STYLE.FRAC
        elif isinstance(expr, patched_rational.PRational):
            return find_repeating_decimal(expr.p, expr.q)
        else:
            style = hasattr(self, 'num_style') and self.num_style or NUM_STYLE.FRAC
        classic_frac = f'{expr.p}/{expr.q}'
        if style & NUM_STYLE.DECIMAL:
            mul, power10 = mul_to_ten_power(expr.q)
            sign = '-' if expr.p < 0 else ''
            if mul:
                num = str(abs(expr.p) * mul).zfill(power10)
                lead = num[:-power10] or '0'
                tail = num[-power10:]
                if len(tail) <= len(classic_frac):
                    return f'{sign}{lead}.{tail}'
        if style & NUM_STYLE.MIXED:  # Важно, if, а не elif!
            sign = '-' if expr.p < 0 else ''
            whole, proper = divmod(abs(expr.p), expr.q)
            whole_s = f'{whole}{NBSP}' if whole != 0 else ''
            return f'{sign}{whole_s}{proper}/{expr.q}'
        return classic_frac

    def _print_Function(self, expr):
        if expr.func.__name__ == 'Abs':
            return f'|{self.stringify(expr.args, ", ")}|'
        if expr.func.__name__ == 'factorial':
            return f'{self.stringify(expr.args, ", ")}!'
        return f'{expr.func.__name__}({self.stringify(expr.args, ", ")})'


_between_two_numbers_p = (
    re.compile(r'[0-9][} ]*(?:\\right)?\)?!?$'),  # search
    re.compile(r'((?:\\left)?\(?-?\d|\\frac{\d+}{\d+})'),  # match
)


class LatexPrinterPatched(LatexPrinter):
    def set_num_style(self, style: NUM_STYLE):
        self.num_style = style

    def _print_Rational(self, expr: Rational):
        if expr.q != 1:
            if isinstance(expr, patched_rational.DRational):
                style = NUM_STYLE.DECIMAL
            elif isinstance(expr, patched_rational.MRational):
                if expr.np != 0:
                    return f'{expr.wp}\\frac{{{expr.np}}}{{{expr.q}}}'
                return f'{expr.wp}'
            elif isinstance(expr, patched_rational.FRational):
                style = NUM_STYLE.FRAC
            elif isinstance(expr, patched_rational.PRational):
                return find_repeating_decimal(expr.p, expr.q)
            else:
                style = hasattr(self, 'num_style') and self.num_style or NUM_STYLE.FRAC
            if style & NUM_STYLE.DECIMAL:
                mul, power10 = mul_to_ten_power(expr.q)
                sign = '-' if expr.p < 0 else ''
                if mul:
                    num = str(abs(expr.p) * mul).zfill(power10)
                    lead = num[:-power10] or '0'
                    tail = num[-power10:]
                    classic_frac = f'{expr.p}/{expr.q}'
                    if len(tail) <= len(classic_frac):
                        return f'{sign}{lead}.{tail}'
            if style & NUM_STYLE.MIXED:  # Важно, if, а не elif!
                sign = '-' if expr.p < 0 else ''
                whole, proper = divmod(abs(expr.p), expr.q)
                whole_s = f'{whole}' if whole != 0 else ''
                if proper != 0:
                    return f'{sign}{whole_s}\\frac{{{proper}}}{{{expr.q}}}'
                return f'{sign}{whole_s}'
            # TODO
            sgn = '-' if expr.p < 0 else ''
            return f'{sgn}\\frac{{{abs(expr.p)}}}{{{expr.q}}}'
            # return f'\\frac{{{expr.p}}}{{{expr.q}}}'
        return self._print(expr.p)

    def _print_Interval(self, i):
        if i.start == i.end:
            return r'\left\{%s\right\}' % self._print(i.start)

        if i.left_open:
            left = '('
        else:
            left = '['

        if i.right_open:
            right = ')'
        else:
            right = ']'

        return r'\left%s%s; %s\right%s' % (left, self._print(i.start), self._print(i.end), right)

    def _convert(self, expr) -> str:
        if not expr.is_Mul:
            return str(self._print(expr))
        args = list(expr.args)

        # If there are quantities or prefixes, append them at the back.
        units, nonunits = sift(
            args,
            lambda x: (hasattr(x, '_scale_factor') or hasattr(x, 'is_physical_constant'))
            or (isinstance(x, Pow) and hasattr(x.base, 'is_physical_constant')),
            binary=True,
        )
        prefixes, units = sift(units, lambda x: hasattr(x, '_scale_factor'), binary=True)
        return self._convert_args(nonunits + prefixes + units)

    def _convert_args(self, args) -> str:
        separator: str = self._settings['mul_symbol_latex']
        numbersep: str = self._settings['mul_symbol_latex_numbers']
        _tex = last_term_tex = ''

        for i, term in enumerate(args):
            term_tex = self._print(term)
            if not (hasattr(term, '_scale_factor') or hasattr(term, 'is_physical_constant')):
                if term.func.__name__ != 'Pr' and self._needs_mul_brackets(  # patched_parenthesis
                    term, first=(i == 0), last=(i == len(args) - 1)
                ):
                    if len(args) > 1 and i == 0 and (term == -1 or term == sympy.core.S.NegativeOne):
                        term_tex = '-'
                    elif len(args) > 1 and i == 0 and not term.is_Add and term.could_extract_minus_sign():
                        # don't parenthesize first of denominator unless singleton
                        pass
                    else:
                        term_tex = r'\left(%s\right)' % term_tex

                if _between_two_numbers_p[0].search(last_term_tex) and _between_two_numbers_p[1].match(term_tex):
                    # between two numbers
                    _tex += numbersep
                elif last_term_tex and term_tex and last_term_tex[-1] == term_tex[0]:
                    _tex += numbersep
                elif _tex:
                    _tex += separator
            elif _tex:
                _tex += separator

            _tex += term_tex
            last_term_tex = term_tex
        return _tex

    def parenthesize(self, item: Expr, level, is_neg=False, strict=False) -> str:
        if isinstance(item, patched_parenthesis.Pr):  # patched_parenthesis
            return self._print(item)
        prec_val = precedence_traditional(item)
        if is_neg and strict:
            return self._add_parens(self._print(item))

        if (prec_val < level) or ((not strict) and prec_val <= level):
            return self._add_parens(self._print(item))
        return self._print(item)

    def _print_Mul(self, expr: Expr):
        # make sure the
        # identities are visible, multiple Rational factors are not combined
        # etc so we display in a straight-forward form that fully preserves all
        # args and their order.
        args = expr.args
        if expr.is_Pow:
            # Pow things like 1/x are printed with _print_Mul  o_O
            n = [sympy.core.S.One]
            neg = -args[1]
            if neg != 1:
                d = [sympy.core.Pow(args[0], -args[1], evaluate=False)]
            else:
                d = [args[0]]
        else:
            d, n = sift(args, lambda x: isinstance(x, Pow) and bool(x.exp.as_coeff_Mul()[0] < 0), binary=True)
            for i, di in enumerate(d):
                if di.exp.is_Number:
                    e = -di.exp
                else:
                    dargs = list(di.exp.args)
                    dargs[0] = -dargs[0]
                    e = Mul._from_args(dargs)
                d[i] = Pow(di.base, e, evaluate=False) if e - 1 else di.base

        nfactors = n or [sympy.core.S.One]
        dfactors = d or [sympy.core.S.One]
        # TODO этот кусок из hum, хз, как его прикрутить, и нужно ли
        # if len(nfactors) > 1 and nfactors[0].could_extract_minus_sign():
        #     nfactors[0] = [self._print(nfactors[0])]
        # if len(dfactors) > 1 and dfactors[0].could_extract_minus_sign():
        #     dfactors[0] = [self._print(dfactors[0])]

        # TODO пока сделаем дичь..
        # if len(nfactors) > 1 and (nfactors[0] == 1 or nfactors[0] == sympy.core.S.One):
        #     nfactors.pop(0)
        # if len(dfactors) > 1 and (dfactors[0] == 1 or dfactors[0] == sympy.core.S.One):
        #     dfactors.pop(0)

        ns = self._convert(sympy.Mul(*nfactors, evaluate=False))
        ds = self._convert(sympy.Mul(*dfactors, evaluate=False))

        dop_space = displaystyle = ''
        fracs_found = 'frac' in ns or 'frac' in ds
        if fracs_found or 'dot' in ns or 'dot' in ds or '^' in ns or '^' in ds:
            displaystyle = 'd'
        if fracs_found:
            dop_space = '\\, ' if fracs_found else ''
        if len(d) > 0:
            return f'\\{displaystyle}frac{{{dop_space}{ns}{dop_space}}}{{{ds}}}'
        return ns

    def _needs_add_brackets(self, expr) -> bool:
        """Returns True if the expression needs to be wrapped in brackets when
        printed as part of an Add, False otherwise.  This is False for most
        things.
        """
        if expr.is_Relational:
            return True
        if expr.has(sympy.core.Mod):
            return True
        if expr.is_Add:
            return True
        return False

    def _print_Add(self, expr, order=None):
        terms = self._as_ordered_terms(expr, order=order)

        tex = ''
        for i, term in enumerate(terms):
            if i == 0:
                pass
            elif term.could_extract_minus_sign():
                tex += ' - '
                term = -term
            else:
                tex += ' + '
            term_tex = self._print(term)
            if (term_tex.startswith('-') and i > 0) or self._needs_add_brackets(term):
                term_tex = r'\left(%s\right)' % term_tex
            tex += term_tex

        return tex


if __name__ == '__main__':
    human_printer = StrPrinterPatched({'order': 'none'})
    latex_printer = LatexPrinterPatched({'order': 'none'})

    print(human_printer.doprint(Rational(7, 3)))

    for num in [Rational(7, 3), Rational(2, 3), Rational(7, 10), Rational(1, 40), Rational(5, 512)]:
        for style in [NUM_STYLE.FRAC, NUM_STYLE.MIXED, NUM_STYLE.DECIMAL, NUM_STYLE.MIXED | NUM_STYLE.DECIMAL]:
            human_printer.set_num_style(style)
            hum = human_printer.doprint(num)
            lat = latex_printer.doprint(num)
            print(f'{style!r:<30} {num!s:<10} == {hum:<10} == {lat:<10}')
