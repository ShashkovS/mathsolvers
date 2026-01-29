import sympy


class PowPatched(sympy.Expr):
    def as_base_exp(self):
        """Return base and exp of self.

        Explanation
        ===========

        If base a Rational less than 1, then return 1/Rational, -exp.
        If this extra processing is not needed, the base and exp
        properties will give the raw arguments.

        Examples
        --------
        >>> from sympy import Pow, S
        >>> p = Pow(S.Half, 2, evaluate=False)
        >>> p.as_base_exp()
        (2, -2)
        >>> p.args
        (1/2, 2)
        >>> p.base, p.exp
        (1/2, 2)

        """
        b, e = self.args
        if b.is_Rational and b.p == 1 and b.q != 1:
            return sympy.Integer(b.q), -e
        # if b.is_Rational and b.p < b.q and b.p > 0:
        #     a=1
        #     return b.__class__(b.q, b.p), -e
        return b, e


sympy.Pow.as_base_exp = PowPatched.as_base_exp
