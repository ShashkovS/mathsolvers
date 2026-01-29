"""mathsolvers"""

from mathsolvers.math_worker import MathWorker
from mathsolvers.mathsolver import solve, solver
from mathsolvers.solvers import (
    FORMAT,
    calc,
    check_equivalence,
    compare,
    strict_compare,
    strict_compare_v2,
    CompareVerdict,
    factor,
    format,
    simplify,
    solve_eq,
    solve_lin_sys,
    solve_single_var,
    subs,
    units,
)

from mathsolvers.solvers_stuff.embedding import embed_solvers
from mathsolvers.solvers_stuff.res_convert import to_text
from mathsolvers.solvers_stuff.math_classification import classify_math
from mathsolvers.sympy_stuff.any_text_parser import check_and_parse
from mathsolvers.sympy_stuff.utils import (
    NUM_STYLE,
    DRational,
    FRational,
    MRational,
    PRational,
    find_global_denominator,
    get_num_style,
    has_significant_change,
    hum,
    is_latex,
    lat,
    lparse,
    parse,
    pparse,
    pprint,
    prepare_eq,
)

from .__about__ import __author__, __copyright__, __license__, __version__

__all__ = [
    '__version__',
    '__author__',
    '__license__',
    '__copyright__',
    'simplify',
    'calc',
    'subs',
    'factor',
    'format',
    'units',
    'compare',
    'strict_compare',
    'strict_compare_v2',
    'CompareVerdict',
    'solver',
    'solve',
    'check_equivalence',
    'solve_eq',
    'solve_lin_sys',
    'solve_single_var',
    'FORMAT',
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
    'embed_solvers',
    'to_text',
    'MathWorker',
    'check_and_parse',
    'classify_math',
]
