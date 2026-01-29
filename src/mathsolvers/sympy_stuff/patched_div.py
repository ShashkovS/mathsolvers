import sympy
from sympy.printing import precedence
from sympy.simplify.simplify import simplify

__all__ = ['PDiv']


class PDiv(sympy.Function):
    extended_real = True
    precedence = precedence.PRECEDENCE['Mul']

    def _to_mul(self):
        return sympy.Mul(self.args[0], sympy.Pow(self.args[1], sympy.S.NegativeOne, evaluate=False), evaluate=False)

    @classmethod
    def eval(cls, arg0, arg1):
        return None

    def _eval_evalf(self, prec):
        return self._to_mul()._eval_evalf(prec)

    def fdiff(self, argindex=1):
        return self._to_mul().fdiff(argindex=argindex)

    def doit(self, deep=True, **hints):
        if deep:
            return self._to_mul().doit(deep=deep, **hints)
        return self._to_mul()

    def _eval_rewrite(self, rule, args, **hints):
        return self._to_mul()

    def _eval_simplify(self, **kwargs):
        return simplify(self._to_mul(), **kwargs)

    def _eval_expand(self, **hints):
        return self._to_mul().expand(**hints)

    def _eval_expand_basic(self, deep=True, **hints):
        if deep:
            return self._to_mul().expand(**hints)
        return self._to_mul()

    def _latex(self, printer, exp=None):
        arg0 = printer.parenthesize(self.args[0], precedence.PRECEDENCE['Mul'])
        arg1 = printer.parenthesize(self.args[1], precedence.PRECEDENCE['Mul'])
        # Из-за какого-то бага или особенности при выводе степени exp передаётся о_О
        if exp is not None:
            return rf'({arg0} \div {arg1})^{{{exp}}}'
        return rf'{arg0} \div {arg1}'

    def _sympystr(self, printer):
        arg0 = printer.parenthesize(self.args[0], precedence.PRECEDENCE['Mul'])
        arg1 = printer.parenthesize(self.args[1], precedence.PRECEDENCE['Mul'])
        return f'{arg0} ÷ {arg1}'

    def _ccode(self, printer):
        arg0 = printer._print(self.args[0])
        arg1 = printer._print(self.args[1])
        return f'PDiv({arg0}, {arg1})'

    def collect(self, syms, func=None, evaluate=True, exact=False, distribute_order_term=True):
        return self._to_mul().collect(
            syms, func=func, evaluate=evaluate, exact=exact, distribute_order_term=distribute_order_term
        )

    def coeff(self, *args, **kwargs):
        return self._to_mul().coeff(*args, **kwargs)


if __name__ == '__main__':
    from sympy import Add, Pow, cos, latex, sin, symbols, tan

    x, y, z = symbols('x y z')

    # Create an expression using PDiv
    for expr in [
        PDiv(10, 5, evaluate=False),
        PDiv(10, 3, evaluate=False),
        PDiv(0, 3, evaluate=False),
        PDiv(x, x, evaluate=False),
        PDiv(x, 2 * x, evaluate=False),
        PDiv(Add(1, 2, evaluate=False), Add(2, 4, evaluate=False)),
        PDiv(2 * x + 2 * y, 2, evaluate=False) - x,
        PDiv(Add(1, -22, evaluate=False), Add(1, -22, evaluate=False)) + 3,
        PDiv(Add(-1, 1, evaluate=False), Add(-1, 1, evaluate=False)),
        PDiv(x - y, 2) * PDiv(x + y, 2),
        PDiv(sin(x), cos(x)) - tan(PDiv(x, 1)),
        Add(x, PDiv(y - x, 1), y, evaluate=False),
        -PDiv(-Pow(3, -2, evaluate=False), -1) - Pow(PDiv(-2, -1), 2, evaluate=False),
        PDiv(PDiv(60, 6), 2),
    ]:
        print(f'{expr=}')
        print(f'{expr.doit()=}')
        print(f'{expr.expand()=}')
        print(f'{expr.simplify()=}')
        print(f'{expr.evalf()=}')
        print(f'{expr > 0=}')
        print(f'{expr >= 0=}')
        print(f'{expr == 0=}')
        print(f'{expr < 0=}')
        print(f'{expr <= 0=}')
        print(f'{latex(expr)=}')
        print('=' * 50)

    # print(solveset(PDiv(x + 1), x))
