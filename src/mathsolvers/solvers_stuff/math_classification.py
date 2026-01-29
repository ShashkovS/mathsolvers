import re
import enum

from mathsolvers.solvers_stuff.units_quantities import re_any_unit
from mathsolvers.solvers_stuff.classes import SolverName

__all__ = ['classify_math']


@enum.unique
class MathST(str, enum.Enum):
    sol_lin_with_roots = 'уравнения с корнями'
    sol_lin_with_parameter = 'линейное с параметром'
    sol_quad_with_parameter = 'квадратное с параметром'
    sol_lin_by_multiplication = 'сводящееся к линейному домножением'
    sol_quad_conversion = 'сводящееся к квадратному'
    sol_lin_by_simplification = 'сводящееся к линейному сокращением'
    sol_quad_inequality = 'квадратное неравенство'
    sol_inequalities_with_variables = 'система неравенств двух и более переменных'
    sol_sol_system_of_two_linear = 'система двух линейных'
    sol_inequality_with_abs = 'неравенство с модулем'
    sol_equation_with_abs = 'уравнение с модулем'
    sol_double_inequality = 'двойное неравенство'
    sol_single_var_inequality_system = 'система неравенств одной переменной'
    sol_factorized = 'разложенное'
    sol_quad_with_discriminant = 'квадратное с дискриминантом'
    sol_linear_inequality = 'линейное неравенство'
    sol_quad_x_squared_equals_c = 'квадратное x² = c'
    sol_quad_x_squared_plus_bx_zero = 'квадратное x² + bx = 0'
    sol_cubic_equation = 'кубическое уравнение'
    sol_high_degree_eq = 'иные уравнения степении ⩾ 3'
    sol_simple_linear_eq = 'простое линейное уравнение'
    sol_unknown_type_eq = 'какое-то непонятное уравнение'
    simp_substitution_eq_ineq = 'подстановка в уравнение или неравенство'
    simp_substitution_expr = 'подстановка в выражение'
    simp_roots = 'корни'
    simp_addition_of_two_numbers = 'сложение 2 чисел'
    simp_arithmetic_two_numbers = 'арифметика 2 чисел'
    simp_arithmetic_no_fractions_or_exponents = 'арифметика без дробей и степеней'
    simp_arithmetic_with_exponents = 'арифметика со степенями'
    simp_arithmetic_with_fractions = 'арифметика с дробями'
    simp_complex_arithmetic = 'много арифметики чисел'
    simp_equation_or_inequality = 'уравнение или неравенство'
    simp_polynomials = 'многочлены'
    simp_factor_simplification = 'сокращение произведений'
    simp_rational_expression_simplification = 'упрощение рац. выражений'
    simp_numbers = 'числа'
    simp_unknown = 'хз'
    u_multiplication = 'умножение'
    u_exponentiation_by_10 = 'со степенью десятки'
    u_units_with_exponents = 'единицы измерения со степенями'
    u_multiple_units = 'в две+ единицы'
    u_speeds = 'скорости'
    u_time_conversion = 'преобразование времени'
    u_with_fraction = 'с дробью'
    u_division = 'деление'
    u_subtraction = 'разность'
    u_addition = 'сложение'
    u_non_integer_no_type = 'нецелое без типа'
    u_non_integer_number = 'нецелое число'
    u_two_units_to_one = '⩾две единицы в одну'
    u_conversion_to_one_type = 'преобразование в один тип'
    c_reverse_order = 'упорядочить в обратном порядке'
    c_multiple_ordering = 'упорядочить много'
    c_measurement_units = 'единицы измерения'
    c_two_roots = 'два корня'
    c_two_exponents = 'две степени'
    c_with_moduli = 'с модулями'
    c_two_sums = 'две суммы'
    c_two_fractions = 'две дроби'
    c_two_decimals = 'два десятичных'
    c_semi_complicated = 'что-то полухитрое'
    c_two_integers = 'два целых'
    f_perc_to_perc = 'perc -> perc'
    f_perc_to_dec_per = 'perc -> dec (periodic)'
    f_perc_to_dec = 'perc -> dec'
    f_perc_to_frac = 'perc -> frac'
    f_perc_to_mix = 'perc -> mix'
    f_dec_per_to_perc = 'dec (periodic) -> perc'
    f_dec_per_to_dec_per = 'dec (periodic) -> dec (periodic)'
    f_dec_per_to_dec = 'dec (periodic) -> dec'
    f_dec_per_to_frac = 'dec (periodic) -> frac'
    f_dec_per_to_mix = 'dec (periodic) -> mix'
    f_dec_to_perc = 'dec -> perc'
    f_dec_to_dec_per = 'dec -> dec (periodic)'
    f_dec_to_dec = 'dec -> dec'
    f_dec_to_frac = 'dec -> frac'
    f_dec_to_mix = 'dec -> mix'
    f_frac_to_perc = 'frac -> perc'
    f_frac_to_dec_per = 'frac -> dec (periodic)'
    f_frac_to_dec = 'frac -> dec'
    f_frac_to_frac = 'frac -> frac'
    f_frac_to_mix = 'frac -> mix'
    f_mix_to_perc = 'mix -> perc'
    f_mix_to_dec_per = 'mix -> dec (periodic)'
    f_mix_to_dec = 'mix -> dec'
    f_mix_to_frac = 'mix -> frac'
    f_mix_to_mix = 'mix -> mix'
    calc = 'calc'
    unknown = 'unknown'

    def __str__(self):
        return self.value


def classify_solve(expr: str, res: dict) -> MathST:
    if 'sqrt' in expr:
        return MathST.sol_lin_with_roots
    if 'eq-linear' in res['sol_codes'] and ('eq-parms-1' in res['sol_codes'] or 'eq-parms-2' in res['sol_codes']):
        return MathST.sol_lin_with_parameter
    if 'eq-quadratic' in res['sol_codes'] and ('eq-parms-1' in res['sol_codes'] or 'eq-parms-2' in res['sol_codes']):
        return MathST.sol_quad_with_parameter
    if 'eq-mul-denom' in res['sol_codes'] and 'eq-linear' in res['sol_codes']:
        return MathST.sol_lin_by_multiplication
    if (
            'eq-mul-denom' in res['sol_codes'] or any(('deg-3' in cd) for cd in res['sol_codes'])
    ) and 'eq-quadratic' in res['sol_codes']:
        return MathST.sol_quad_conversion
    if 'eq-linear' in res['sol_codes'] and any(('deg-2' in cd) or ('deg-3' in cd) for cd in res['sol_codes']):
        return MathST.sol_lin_by_simplification
    if 'uneq-unknown' in res['sol_codes'] and any(('deg-2' in cd) or ('deg-3' in cd) for cd in res['sol_codes']):
        return MathST.sol_quad_inequality
    if (
            'solve-sys-2-eq' in res['sol_codes']
            and 'solve-sys-2-vars' in res['sol_codes']
            and len(re.findall(r'>=|<=|>|<|\\le|\\ge', expr.strip('<> '))) >= 2
    ):
        return MathST.sol_inequalities_with_variables
    if 'solve-sys-2-eq' in res['sol_codes'] and 'solve-sys-2-vars' in res['sol_codes']:
        return MathST.sol_sol_system_of_two_linear
    if '|' in expr and 'uneq-unknown' in res['sol_codes']:
        return MathST.sol_inequality_with_abs
    if '|' in expr:
        return MathST.sol_equation_with_abs
    if '////' not in expr and len(re.findall(r'>=|<=|>|<|\\le|\\ge', expr.strip('<> '))) >= 2:
        return MathST.sol_double_inequality
    if 'solve-sys-ineqs-one-var' in res['sol_codes'] and 'solve-sys-2-eq' in res['sol_codes']:
        return MathST.sol_single_var_inequality_system
    if 'sol-eq-mul-lin' in res['sol_codes']:
        return MathST.sol_factorized
    if 'eq-quadr-discr' in res['sol_codes']:
        return MathST.sol_quad_with_discriminant
    if 'uneq-unknown' in res['sol_codes']:
        return MathST.sol_linear_inequality
    if 'eq-quadr-x^2=c' in res['sol_codes']:
        return MathST.sol_quad_x_squared_equals_c
    if 'eq-quadr-x(x-b)' in res['sol_codes']:
        return MathST.sol_quad_x_squared_plus_bx_zero
    if 'eq-unknown-deg-3' in res['sol_codes']:
        return MathST.sol_cubic_equation
    if (
            'eq-unknown-deg-4' in res['sol_codes']
            or 'eq-unknown-deg-5' in res['sol_codes']
            or 'eq-unknown-deg-6' in res['sol_codes']
            or 'eq-unknown-deg-7' in res['sol_codes']
            or 'eq-unknown-deg-8' in res['sol_codes']
    ):
        return MathST.sol_high_degree_eq
    if 'solve-sys-eqs' in res['sol_codes']:
        return MathST.sol_sol_system_of_two_linear
    if 'eq-parms-0' in res['sol_codes'] and 'eq-linear' in res['sol_codes']:
        return MathST.sol_simple_linear_eq
    return MathST.sol_unknown_type_eq


def classify_simplify(expr: str, res: dict) -> MathST:
    if re.search(r'^<<[^\\]*(>=|<=|>|<|=|\\le|\\ge).*\\\\', expr):
        return MathST.simp_substitution_eq_ineq
    if '\\\\' in expr:
        return MathST.simp_substitution_expr
    if 'sqrt' in expr:
        return MathST.simp_roots
    if (
            'simpl-no-vars' in res['sol_codes']
            and len(re.findall(r'\+', expr)) == 1
            and len(re.findall(r'\-|\*|dot|div|frac|\/|\^|:|!|⋅', expr)) == 0
    ):
        return MathST.simp_addition_of_two_numbers
    if 'simpl-no-vars' in res['sol_codes'] and len(re.findall(r'\+|\-|\*|dot|div|frac|\/|\^|:|⋅', expr)) == 1:
        return MathST.simp_arithmetic_two_numbers
    if 'simpl-no-vars' in res['sol_codes'] and 'frac' not in expr and '/' not in expr and '^' not in expr:
        return MathST.simp_arithmetic_no_fractions_or_exponents
    if 'simpl-no-vars' in res['sol_codes'] and '^' in expr:
        return MathST.simp_arithmetic_with_exponents
    if (
            'simpl-no-vars' in res['sol_codes']
            and 'frac' in expr
            and len(re.findall(r'\-|\*|dot|div|frac|\/|\^|:|!|⋅', expr)) < 6
    ):
        return MathST.simp_arithmetic_with_fractions
    if 'simpl-no-vars' in res['sol_codes']:
        return MathST.simp_complex_arithmetic
    if re.search(r'[^\\]*(>=|<=|>|<|=|\\le|\\ge).*', expr.strip('<> =')):
        return MathST.simp_equation_or_inequality
    if (
            'frac' not in re.sub(r'\\frac\{\s*[-+]?\d+\s*\}\{\s*[-+]?\d+\s*\}', '', expr)
            and ':' not in expr
            and '/' not in expr
            and len(re.findall(r'\^\s*\{\s*-', expr)) == 0
    ):
        return MathST.simp_polynomials
    if '+' not in expr and '-' not in re.sub(r'\{\s*-\s*\d+\}', '', expr):
        return MathST.simp_factor_simplification
    return MathST.simp_rational_expression_simplification


def classify_factor(expr: str, res: dict) -> MathST:
    if 'factor-int' in res['sol_codes']:
        return MathST.simp_numbers
    return MathST.simp_unknown


def classify_units(expr: str, res: dict) -> MathST:
    if '*' in expr or 'dot' in expr or '⋅' in expr:
        return MathST.u_multiplication
    if re.search(r'10\s*^\s*\{?(?:\d\d|[7-9])', expr):
        return MathST.u_exponentiation_by_10
    if res['sol_codes'] == ['units-simple'] and re.search(r'\w\s*\}?\s*(?:\^|\*\*)\s*\{?\s*\d', expr):
        return MathST.u_units_with_exponents
    if expr.count('\\\\') >= 2:
        return MathST.u_multiple_units
    if re.search(r'(?:м|км)\s*\/\s*(?:ч|мин|с|c)', expr):
        return MathST.u_speeds
    if re.search(r'(?:год|лет|мес|нед|сут|час|ч|мин|с|c)', expr):
        return MathST.u_time_conversion
    if 'frac' in expr:
        return MathST.u_with_fraction
    if ':' in expr or 'div' in expr or '/' in expr:
        return MathST.u_division
    if '-' in expr:
        return MathST.u_subtraction
    if '+' in expr:
        return MathST.u_addition
    if ('.' in expr or ',' in expr) and '\\\\' not in expr:
        return MathST.u_non_integer_no_type
    if '.' in expr or ',' in expr:
        return MathST.u_non_integer_number
    if len(re_any_unit.findall(expr)) >= 3:
        return MathST.u_two_units_to_one
    return MathST.u_conversion_to_one_type


def classify_format(expr: str, res: dict) -> MathST:
    frm = '?'
    if '%' in expr or 'format-from-perc' in res['sol_codes']:
        frm = 'perc'
    elif 'format-from-periodic' in res['sol_codes']:
        frm = 'dec_per'
    elif 'format-from-dec' in res['sol_codes']:
        frm = 'dec'
    elif 'format-from-frac' in res['sol_codes']:
        frm = 'frac'
    elif 'format-from-mix' in res['sol_codes']:
        frm = 'mix'
    to = '?'
    if 'format-to-periodic' in res['sol_codes']:
        to = 'dec_per'
    elif 'format-to-frac' in res['sol_codes']:
        to = 'frac'
    elif 'format-to-mix' in res['sol_codes']:
        to = 'mix'
    elif 'format-to-dec' in res['sol_codes']:
        to = 'dec'
    elif 'format-to-perc' in res['sol_codes']:
        to = 'perc'
    conv = f'f_{frm}_to_{to}'
    return MathST[conv]


def classify_compare(expr: str, res: dict) -> MathST:
    if 'reverse' in expr:
        return MathST.c_reverse_order
    if expr.count('\\\\') > 1:
        return MathST.c_multiple_ordering
    if re_any_unit.search(expr):
        return MathST.c_measurement_units
    if expr.count('sqrt') >= 2:
        return MathST.c_two_roots
    if expr.count('^') >= 2:
        return MathST.c_two_exponents
    if expr.count('|') >= 1:
        return MathST.c_with_moduli
    if expr.count('+') + expr.count('-') >= 2:
        return MathST.c_two_sums
    if expr.count('frac') >= 2:
        return MathST.c_two_fractions
    if expr.count('.') + expr.count(',') >= 2:
        return MathST.c_two_decimals
    if (
            expr.count('.')
            + expr.count(',')
            + expr.count('frac') * 2
            + expr.count('^')
            + expr.count('+')
            + expr.count('sqrt') * 2
            + expr.count('-')
            + expr.count(':')
            >= 2
    ):
        return MathST.c_semi_complicated
    return MathST.c_two_integers


def classify_math(solver: SolverName, expr: str, res: dict) -> MathST:
    if solver == 'solve':
        subtype = classify_solve(expr, res)
    elif solver == 'simplify':
        subtype = classify_simplify(expr, res)
    elif solver == 'factor':
        subtype = classify_factor(expr, res)
    elif solver == 'units':
        subtype = classify_units(expr, res)
    elif solver == 'format':
        subtype = classify_format(expr, res)
    elif solver == 'compare':
        subtype = classify_compare(expr, res)
    elif solver == 'calc':
        subtype = MathST.calc
    else:
        subtype = MathST.unknown
    return subtype
