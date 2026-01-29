import sympy
from sympy.simplify.simplify import simplify

__all__ = ['Pr']


def _inverser(pr):
    if isinstance(pr, sympy.Expr):
        if pr.is_Atom:
            return pr
        return pr.args[0]
    return pr


class Pr(sympy.Function):
    extended_real = True

    @classmethod
    def eval(cls, arg):
        return None

    def _eval_evalf(self, prec):
        return self.args[0]._eval_evalf(prec)

    def fdiff(self, argindex=1):
        return self.args[0]

    def inverse(self, argindex=1):
        return _inverser

    def doit(self, deep=True, **hints):
        if deep:
            return self.args[0].doit(deep=deep, **hints)
        return self.args[0]

    def _eval_rewrite(self, rule, args, **hints):
        return args[0]

    def _eval_simplify(self, **kwargs):
        return simplify(self.args[0], **kwargs)

    def _eval_expand(self, **hints):
        return self.args[0].expand(**hints)

    def _eval_expand_basic(self, deep=True, **hints):
        if deep:
            return self.args[0].expand(**hints)
        return self.args[0]

    def _latex(self, printer, exp=None):
        # Из-за какого-то бага или особенности при выводе степени exp передаётся о_О
        arg = printer._print(self.args[0])
        if exp:
            return rf'({arg})^{{{exp}}}'
        return rf'({arg})'  # (для модельки удобнее без left/right) rf"\left({arg}\right)"

    def _sympystr(self, printer):
        arg = printer._print(self.args[0])
        return f'({arg})'

    def _ccode(self, printer):
        arg = printer._print(self.args[0])
        return f'({arg})'

    def collect(self, syms, func=None, evaluate=True, exact=False, distribute_order_term=True):
        return self.args[0].collect(
            syms, func=func, evaluate=evaluate, exact=exact, distribute_order_term=distribute_order_term
        )

    def coeff(self, *args, **kwargs):
        return self.args[0].coeff(*args, **kwargs)


if __name__ == '__main__':
    from sympy import Add, Pow, latex, sin, solveset, symbols

    # Define symbols
    x, y, z = symbols('x y z')

    term = Pr(Add(x, 2))
    term.collect(x)
    a = term.coeff(x, 1)
    b = term.coeff(x, 0)
    print(f'{a}x + {b}')

    # Create an expression using Pr
    for expr in [
        Pr(Add(1, 2, evaluate=False)) + 3,
        Pr(x + y, evaluate=False) - x,
        Pr(Add(1, -22, evaluate=False)) + 3,
        Pr(Add(-1, 1, evaluate=False)),
        Pr(x - y) * Pr(x + y),
        Pr(sin(x)) - sin(Pr(x)),
        Add(x, Pr(y - x), y, evaluate=False),
        -Pow(3, -2, evaluate=False) - Pow(Pr(-2), 2, evaluate=False),
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

    print(solveset(Pr(x + 1), x))
