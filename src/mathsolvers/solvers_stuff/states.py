import re

import sympy

from mathsolvers.solvers import simplification
from mathsolvers.solvers_stuff import classes
from mathsolvers.sympy_stuff import utils

op_re = re.compile(r'([<>]=?|==?)')


class EquationState:
    expr: str
    op: str
    left: sympy.Expr
    right: sympy.Expr
    left_s: str
    right_s: str
    left_changes_sbs: str | None
    right_changes_sbs: str | None
    prev_left: sympy.Expr | None
    prev_right: sympy.Expr | None
    prev_left_s: str | None
    prev_right_s: str | None
    error: str | None
    vars: list[sympy.Symbol]
    diff: sympy.Expr
    ns: utils.NUM_STYLE
    x: sympy.Symbol | None
    deg: int | None = -1
    roots: list[sympy.Expr] = []
    lcm_denom: sympy.Expr | None = 1
    lcm_denom_s: str | None = '1'

    def __init__(self, expr: str):
        self.expr = expr
        expr = utils.le_re.sub(' <= ', expr)
        expr = utils.ge_re.sub(' >= ', expr)
        expr = utils.lt_re.sub(' < ', expr)
        expr = utils.gt_re.sub(' > ', expr)
        self.error = None
        parts = op_re.split(expr)
        if len(parts) != 3:
            self.error = f'В выражении «{expr}» должен быть ровно один оператор: «=» или <,<=, >, >='
            return
        left, self.op, right = parts
        if self.op == '==':
            self.op = '='

        try:
            self.left = utils.parse(left)
        except Exception:
            self.error = f'Левая часть «{left}» не парсится'
            return
        try:
            self.right = utils.parse(right)
        except Exception:
            self.error = f'Правая часть «{right}» не парсится'
            return

        self.vars = sorted((self.left.free_symbols | self.right.free_symbols), key=lambda v: v.name)
        self.ns = utils.get_num_style(expr)
        self.diff = (self.left - self.right).expand()
        self.left_s = utils.lat(self.left, self.ns)
        self.right_s = utils.lat(self.right, self.ns)
        self.roots = []

    def set_var(self, x: sympy.Symbol | None = None):
        if x:
            pass
        elif self.vars:
            self.x = self.vars[-1]
        else:
            self.x = utils.parse('x')
        try:
            self.deg = sympy.degree(self.diff, self.x)
        except Exception:
            self.deg = -1
        return self.x

    def __iadd__(self, other):
        self._upd_prev()
        self.left = sympy.Add(self.left, other, evaluate=False)
        self.right = sympy.Add(self.right, other, evaluate=False)
        self._simplify()
        return self

    def __isub__(self, other):
        self._upd_prev()
        sb = sympy.Mul(-1, other)
        self.left = sympy.Add(self.left, sb, evaluate=False)
        self.right = sympy.Add(self.right, sb, evaluate=False)
        self._simplify()
        return self

    def __imul__(self, other):
        self._upd_prev()
        self.left = sympy.Mul(self.left, other, evaluate=False)
        self.right = sympy.Mul(self.right, other, evaluate=False)
        self.diff = (self.diff * other).simplify()
        self._simplify()
        return self

    def __itruediv__(self, other):
        self._upd_prev()
        self.left = utils.PDiv(self.left, other, evaluate=False)
        self.right = utils.PDiv(self.right, other, evaluate=False)
        self.diff = utils.PDiv(self.diff, other).simplify()
        self._simplify()
        return self

    def swap(self):
        self._upd_prev()
        self.left, self.right = self.right, self.left
        self.left_s, self.right_s = self.right_s, self.left_s
        self.diff *= -1

    def find_denom_and_mul(self, max_lcm_denom=-1):
        # max_lcm_denom < 1 => на чисто числовые множители домножать не будем
        self.lcm_denom = lcm_denom = utils.find_global_denominator(self.left, self.right)
        self.lcm_denom_s = lcm_denom_s = utils.lat(lcm_denom, self.ns)
        if lcm_denom != 1 and (lcm_denom.free_symbols or abs(lcm_denom) <= max_lcm_denom):
            lcm_denom_pr = lcm_denom
            if lcm_denom_pr.is_Mul:
                lcm_denom_pr = utils.Pr(lcm_denom, evaluate=False)
            self._upd_prev()
            self.left = sympy.Mul(self.left, lcm_denom_pr, evaluate=False)
            self.right = sympy.Mul(self.right, lcm_denom_pr, evaluate=False)
            self.left_changes_sbs, self.left = simplification.step_by_step_str_and_res(self.left, self.ns,
                                                                                       fin_simplify=True,
                                                                                       fix_expand=True)
            self.right_changes_sbs, self.right = simplification.step_by_step_str_and_res(self.right, self.ns,
                                                                                         fin_simplify=True,
                                                                                         fix_expand=True)
            # В целом после упрощения порядок нормализован. Но только в том случае, если какие-либо преобразования были.
            self.left = utils.normalize_terms_order(self.left)
            self.right = utils.normalize_terms_order(self.right)
            self.left_s = utils.lat(self.left, self.ns)
            self.right_s = utils.lat(self.right, self.ns)
            if '=' not in self.left_changes_sbs:
                self.left_changes_sbs = fr'{self.prev_left_s} \cdot {self.lcm_denom_s} = {self.left_s}'
            if '=' not in self.right_changes_sbs:
                self.right_changes_sbs = fr'{self.prev_right_s} \cdot {self.lcm_denom_s} = {self.right_s}'
            self.diff = (self.diff * lcm_denom).simplify()
        else:
            self.lcm_denom = lcm_denom = 1
            self.lcm_denom_s = lcm_denom_s = '1'
        return lcm_denom, lcm_denom_s

    def simplify(self):
        self._upd_prev()
        self._simplify()

    def factor(self):
        self.left = sympy.factor(self.left)
        self.right = sympy.factor(self.right)
        if self.left.is_Mul:
            self.left = sympy.Mul(*(utils.normalize_terms_order(term) for term in self.left.args), evaluate=False)
        if self.right.is_Mul:
            self.right = sympy.Mul(*(utils.normalize_terms_order(term) for term in self.right.args), evaluate=False)
        self.left_s = utils.lat(self.left, self.ns)
        self.right_s = utils.lat(self.right, self.ns)
        self.left_changes_sbs = f'{self.prev_left_s} = {self.left_s}'
        self.right_changes_sbs = f'{self.prev_right_s} = {self.right_s}'

    def _upd_prev(self):
        self.prev_left = self.left
        self.prev_right = self.right
        self.prev_left_s = self.left_s
        self.prev_right_s = self.right_s

    def _simplify(self):
        self.left_changes_sbs, self.left = simplification.step_by_step_str_and_res(
            self.left, self.ns, fin_simplify=True, fix_expand=True
        )
        self.right_changes_sbs, self.right = simplification.step_by_step_str_and_res(
            self.right, self.ns, fin_simplify=True, fix_expand=True
        )
        # Вот эта хрень из-за проблемы с ±1, которые могут остаться множителями.
        # Потенциально может приводить к проблемам :(
        # TODO починить бы это всё
        self.left = utils.normalize_terms_order(self.left.doit().expand())
        self.right = utils.normalize_terms_order(self.right.doit().expand())
        self.left_s = utils.lat(self.left, self.ns)
        self.right_s = utils.lat(self.right, self.ns)
        self.diff = (self.left - self.right).expand()
        self.set_var(self.x)

    def __str__(self):
        return f'{self.left_s} {self.op} {self.right_s}'


class SolutionState:
    expr: str | None
    exprs: list[str] | None
    eq: EquationState | None
    eqs: list[EquationState] | None
    error: str | None
    steps: list[classes.Step]
    sol: list[dict]
    final_answer: str | None
    x: sympy.Symbol | None
    vars: list[sympy.Symbol] | None
    ns: utils.NUM_STYLE
    sol_codes: list[str]
    good_scheme: bool | None = None

    def __init__(self, expr: str | None = None, exprs: list[str] | None = None):
        self.steps = []
        self.sol = []
        self.expr = expr
        self.exprs = exprs
        self.error = None
        self.sol_codes = []

    def add_step(self, action: str, solution: str, answer: str):
        self.steps.append(classes.Step(action=action, solution=solution, answer=answer))

    def as_dict(self):
        res = {'task': self.expr if self.expr else r' \\ '.join(self.exprs)}
        if self.error:
            res['error'] = self.error
            return res
        res['final_answer'] = self.final_answer
        res['sol'] = self.sol
        for i, step in enumerate(self.steps, start=1):
            res[f'step {i}'] = step
        if self.sol_codes:
            res['sol_codes'] = self.sol_codes
        res['good_scheme'] = self.good_scheme
        return res
