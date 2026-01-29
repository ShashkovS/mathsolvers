# MathSolvers

MathSolvers is a Python package for solving, simplifying, and comparing math expressions with step-by-step explanations. It accepts plain text, LaTeX, and mixed Unicode math input (e.g. `×`, `÷`, `√`, decimal commas), and returns structured results or readable text.

## Installation

Python 3.10+ is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development (tests, linting, tooling):

```bash
pip install -e .[dev]
```

## Quick Start

```python
import mathsolvers as ms

result = ms.solver('<<solve 2x+1=3>>')
print(result['final_answer'])
print(ms.to_text(result))
```

Embed multiple solvers inside arbitrary text:

```python
text = """
Find x: <<solve 2x+1=3>>
Compute: <<calc 7 // 2>> (rem <<calc 7 % 2>>)
"""
print(ms.embed_solvers(text))
```

## Detailed Examples

### Solve with step-by-step output

```python
import mathsolvers
mathsolvers.pprint(mathsolvers.solver('<<solve 2x+1=3>>'))
```

Example output:

```
{ 'task': '2x+1=3',
  'final_answer': '$x = 1$',
  'sol': [{'x': '1'}],
  'step 1': { 'action': 'Перенесём $1$ из левой части в правую.',
              'solution': 'Перенесём $1$ из левой части в правую. Для этого нужно из обеих частей вычесть $1$:\n'
                          '$2 \\cdot x + 1 - 1 = 3 - 1$\n'
                          '$2 \\cdot x = 2$',
              'answer': '$2 \\cdot x = 2$'},
  'step 2': { 'action': 'Поделим обе части уравнения на $2$',
              'solution': 'Поделим обе части уравнения на $2$. Cлева коэффициент сократится, получится просто $x$:\n'
                          '$\\frac{2 \\cdot x}{2} = \\frac{2}{2}$\n'
                          '$x = 1$',
              'answer': '$x = 1$'}}
```

### Render a solution as plain text

```python
import mathsolvers
print(mathsolvers.to_text(mathsolvers.solver('<<solve 2x+1=3>>')))
```

```
1
action
Перенесём $1$ из левой части в правую.
solution
Перенесём $1$ из левой части в правую. Для этого нужно из обеих частей вычесть $1$:
$2 \cdot x + 1 - 1 = 3 - 1$
$2 \cdot x = 2$
answer
$2 \cdot x = 2$
2
action
Поделим обе части уравнения на $2$
solution
Поделим обе части уравнения на $2$. Cлева коэффициент сократится, получится просто $x$:
$\frac{2 \cdot x}{2} = \frac{2}{2}$
$x = 1$
answer
$x = 1$
final_answer
$x = 1$
```

### Embed solvers into a narrative text

```python
import mathsolvers
print(mathsolvers.embed_solvers("""
1
action
Посчитаем: $<<calc 2+3>>$. Теперь решим уравнение.
solution
Уравнение будет $2x+1=3$
answer
$2x+1=3$

<<solve 2x+1=3>>
"""))
```

```
1
action
Посчитаем: $2 + 3 = 5$. Теперь решим уравнение.
solution
Уравнение будет $2x+1=3$
answer
$2x+1=3$
2
action
Перенесём $1$ из левой части в правую.
solution
Перенесём $1$ из левой части в правую. Для этого нужно из обеих частей вычесть $1$:
$2 \cdot x + 1 - 1 = 3 - 1$
$2 \cdot x = 2$
answer
$2 \cdot x = 2$
3
action
Поделим обе части уравнения на $2$
solution
Поделим обе части уравнения на $2$. Cлева коэффициент сократится, получится просто $x$:
$\frac{2 \cdot x}{2} = \frac{2}{2}$
$x = 1$
answer
$x = 1$
final_answer
$x = 1$
```

## Solver Call Syntax

Solver calls are written inside `<<...>>` (also `«...»` and `[[...]]` are accepted). Multiple parameters are separated by `\\`.

Common calls:

- `<<solve 2x+1=3>>`
- `<<solve 2x+3=y \\ y-1=4x>>` (system)
- `<<solve 2 < 2x < 7>>` (chained inequality)
- `<<simplify (1+x)/(2+3x) \\ x=3>>` (substitution)
- `<<calc 24,5 \div 5>>`
- `<<factor x^2 + 2x + 1>>`
- `<<units 2м 12см + 3м 90см>>`
- `<<units 340см \\ дм>>` (convert units)
- `<<format 1 \frac{1}{2} \\ dec>>` (number format)
- `<<compare \frac{3}{5} \\ \frac{2}{7} \\ \frac{3}{4}>>`

`solver()` accepts a string with multiple calls or a list of calls; it merges steps and joins `final_answer` with `;`.

## Core Python API

High-level entry points (exposed in `mathsolvers.__init__`):

- `solver(text_or_calls)` — parse `<<...>>` calls and return a dict result.
- `solve(expr, *more, vars=None)` — solve equation/inequality or a system.
- `simplify(expr)` / `calc(expr)` / `subs(expr, vals)` / `factor(expr)` / `units(expr, to_units)` / `format(expr, fmt)` / `compare(exprs)`.
- `embed_solvers(text)` — replace solver calls inside text with results.
- `to_text(result)` — render a solver result dict as readable text.
- `check_equivalence(expr1, expr2)` — compare expressions or relations.
- `strict_compare_v2(expr1, expr2)` — robust answer checking; returns `CompareVerdict` (`EQUAL`, `MAY_BE`, `NOT_EQUAL`, `ERROR`).
- `check_and_parse(text)` — detect if free-form text can be converted into a solver call.

Example: strict comparison

```python
from mathsolvers import strict_compare_v2, CompareVerdict

verdict = strict_compare_v2("1 + 2*3", "3\cdot2 + 1")
assert verdict == CompareVerdict.EQUAL
```

More examples:

```python
from mathsolvers import strict_compare_v2, CompareVerdict
assert strict_compare_v2("2", "$2.0$") == CompareVerdict.EQUAL
assert strict_compare_v2("1 + 2 * 3", "\\( 3 \\times 2 + 1 \\)") == CompareVerdict.EQUAL
assert strict_compare_v2("2 метра", "2") == CompareVerdict.EQUAL
assert strict_compare_v2("2", "4") == CompareVerdict.NOT_EQUAL
assert strict_compare_v2("4", "2+2") == CompareVerdict.MAY_BE
assert strict_compare_v2("2", "чё за?") == CompareVerdict.ERROR
```

## Parsing & Formatting Utilities

Low-level helpers live in `mathsolvers.sympy_stuff.utils`:

- `parse(expr)` / `parse_and_ns(expr)` — parse into a SymPy expression; `parse_and_ns` also returns a `NUM_STYLE` hint.
- `hum(expr)` / `lat(expr)` — render SymPy expressions to human-readable or LaTeX strings.

Example (as used in tests and analysis code):

```python
import mathsolvers as ms
from mathsolvers.solvers.simplification import step_by_step_and_res
from mathsolvers.sympy_stuff.utils import parse_and_ns, hum, lat

expr = "1 1/3 + 2/3"
parsed, ns = parse_and_ns(expr)
steps, res = step_by_step_and_res(parsed, ns)
print(hum(res, ns))
print(lat(res, ns))
```

Example: apply a heuristic on the simplification trace and numeric result:

```python
import sympy
from mathsolvers.solvers.simplification import step_by_step_and_res
from mathsolvers.sympy_stuff.utils import parse_and_ns

expr = "2 + 1/3 + 1/3 + 1/3"
parsed, ns = parse_and_ns(expr)
steps, res = step_by_step_and_res(parsed, ns)

if 6 <= len(steps) <= 6 and res.is_Rational and 3 <= res.q <= 9 and 1 <= res.p // res.q <= 7:
    print("Matches heuristic:", res)
```

The simplifier also exposes `step_by_step_and_res` and `step_by_step_str` for stepwise simplification results.

## Parse Free-Form Tasks

`check_and_parse` tries to recognize a full task statement and produce a solver call.

```python
from mathsolvers import check_and_parse

print(check_and_parse('Как упростить выражение: (9^6 * (-4)^5)/(-6)^10'))
print(check_and_parse('2м + x = 5м'))
print(check_and_parse('привет'))
```

Typical output shape:

```
class ParseResult(TypedDict):
    expr: str
    parsed: sympy.Expr
    solver_call: str
```

## Output Format Notes

### Equations and systems (`solve`)

Examples of `final_answer`:

```
$x = -5$
$a = \frac{19}{10}$
$b = 1\frac{5}{12}$
$p = 7,1$
Корней нет
$x$ — любое
```

Systems list solutions in lexicographic variable order:

```
$x = 1, y = 5$
x=1,y=2;x=1,y=3
```

### Inequalities

```
$x \in (2; \infty)$
$x \in (-\infty; -5]$
$x \in (-3; 4\sqrt{3}]$
$x \in (-3; -2) \cup (3; \infty)$
```

## MathWorker (Timeout Isolation)

Use `MathWorker` to run computations in a separate process with a timeout:

```python
from mathsolvers import MathWorker

worker = MathWorker()
try:
    res = worker.solver('<<simplify 2**100>>', timeout=3)
finally:
    worker.shutdown()
```

## Testing

Tests are pytest-based and configured for parallel runs (`-n7`) with a 5s per-test timeout.

```bash
python -m pytest
```

You can also run the bundled runner:

```bash
python tests/run_all_tests.py
```

## Supported Input Highlights

- Mixed fractions: `1 2/3`, LaTeX `\frac{7}{2}`
- Decimal commas: `2,5`
- Repeating decimals: `0,(3)`
- Unicode ops: `×`, `·`, `÷`, `√`, `−`
- Implicit multiplication: `2x`, `(x+1)(x-1)`

If input cannot be parsed, the result dict includes an `error` field.
