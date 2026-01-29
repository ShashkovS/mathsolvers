import sympy
from sympy.core import numbers

NBSP = '\xa0'
__all__ = ['MRational', 'DRational', 'FRational', 'PRational']


class _Op_wrapper(sympy.core.numbers.Rational):
    def __neg__(self):
        return self.__class__(-self.p, self.q, 1)

    def __iadd__(self, other):
        if isinstance(other, (int, numbers.Integer, numbers.One, numbers.Zero, numbers.NegativeOne)):
            return self.__class__(int(self.p + self.q * other), self.q)
        if isinstance(other, numbers.Rational):
            return self.__class__(int(self.p * other.q + self.q * other.p), int(self.q * other.q))
        return NotImplemented

    def __isub__(self, other):
        if isinstance(other, (int, numbers.Integer, numbers.One, numbers.Zero, numbers.NegativeOne)):
            return self.__class__(int(self.p - self.q * other), self.q)
        if isinstance(other, numbers.Rational):
            return self.__class__(int(self.p * other.q - self.q * other.p), int(self.q * other.q))
        return NotImplemented

    def __imul__(self, other):
        if isinstance(other, (int, numbers.Integer, numbers.One, numbers.Zero, numbers.NegativeOne)):
            return self.__class__(int(self.p * other), self.q)
        if isinstance(other, numbers.Rational):
            return self.__class__(int(self.p * other.p), int(self.q * other.q))
        return NotImplemented

    def __add__(self, other):
        return self.__iadd__(other)

    def __radd__(self, other):
        return self.__iadd__(other)

    def __sub__(self, other):
        return self.__isub__(other)

    def __rsub__(self, other):
        return self.__class__(-self.p, self.q, 1).__iadd__(other)

    def __mul__(self, other):
        return self.__imul__(other)

    def __rmul__(self, other):
        return self.__imul__(other)


class MRational(_Op_wrapper):
    wp: int  # whole part
    np: int  # numerator (original)
    __slots__ = ('p', 'q', 'wp', 'np')

    def __new__(cls, wp: int, np: int, dp: int = None):
        obj = sympy.Expr.__new__(cls)
        wp = int(wp)
        np = int(np)
        sgn = -1 if wp < 0 or np < 0 else 1
        if dp is not None:
            dp = int(dp)
            obj.wp = wp
            obj.np = np
            obj.p = sgn * (abs(wp) * dp + abs(np))
            obj.q = dp
        else:
            obj.p = wp
            obj.q = np
            obj.wp, obj.np = divmod(abs(wp), np)
            obj.wp *= sgn
            if obj.wp == 0:
                obj.np *= sgn
        if obj.p == 0:
            obj = sympy.core.numbers.Zero
        return obj

    def __neg__(self):
        return self.__class__(-self.wp, self.np, self.q)

    def __mul__(self, other):
        if isinstance(other, (numbers.One, numbers.NegativeOne)):
            return self.__class__(int(self.wp * other), self.np, self.q)
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, (numbers.One, numbers.NegativeOne)):
            return self.__class__(int(self.wp * other), self.np, self.q)
        if isinstance(other, int):
            sgn = -1 if self.wp < 0 or self.np < 0 else 1
            newp = (abs(self.wp) * self.q + abs(self.np)) * other
            new_sign = sgn * (-1 if other < 0 else 1)
            new_wp, new_p = divmod(abs(newp), self.q)
            return self.__class__(new_sign * new_wp, new_p * (1 if new_wp != 0 else new_sign), self.q)
        return NotImplemented

    # def _sympystr(self, printer):
    #     sgn = '-' if self.p < 0 else ''
    #     if self.q == 1:
    #         return str(self.p)
    #     elif self.wp == 0:
    #         return f'{self.p}/{self.q}'
    #     else:
    #         return f'{sgn}{self.wp}{NBSP}{abs(self.np)}{self.q}'
    #
    # def _latex(self, printer):
    #     sgn = '-' if self.p < 0 else ''
    #     if self.q == 1:
    #         return str(self.p)
    #     elif self.wp == 0:
    #         return f'{sgn}\\frac{{{abs(self.p)}}}{{{self.q}}}'
    #     else:
    #         return f'{sgn}{self.wp}\\frac{{{abs(self.p)}}}{{{self.q}}}'


class DRational(_Op_wrapper):
    pass


class FRational(_Op_wrapper):
    pass
    # def _sympystr(self, printer):
    #     sgn = '-' if self.p < 0 else ''
    #     if self.q == 1:
    #         return str(self.p)
    #     else:
    #         return f'{self.p}/{self.q}'
    #
    # def _latex(self, printer):
    #     sgn = '-' if self.p < 0 else ''
    #     if self.q == 1:
    #         return str(self.p)
    #     else:
    #         return f'{sgn}\\frac{{{abs(self.p)}}}{{{self.q}}}'


class PRational(_Op_wrapper):
    # text_repr: str
    # __slots__ = ('p', 'q', 'text_repr')
    pass
