import ast

from sympy.parsing import sympy_parser


class EvaluateFalseTransformerPatched(ast.NodeTransformer):
    # Определяем операторы; для неявного умножения используем отдельный оператор IMul
    operators = {
        ast.Add: 'Add',
        ast.Mult: 'Mul',
        ast.Pow: 'Pow',
        ast.Sub: 'Add',
        ast.Div: 'Mul',
        ast.BitOr: 'Or',
        ast.BitAnd: 'And',
        ast.BitXor: 'Not',
        ast.Mod: 'Mod',  # patch
        ast.FloorDiv: 'PDiv',  # patch
        ast.MatMult: 'IMul',  # неявное умножение – отдельный оператор
    }
    functions = (
        'Abs',
        'im',
        're',
        'sign',
        'arg',
        'conjugate',
        'acos',
        'acot',
        'acsc',
        'asec',
        'asin',
        'atan',
        'acosh',
        'acoth',
        'acsch',
        'asech',
        'asinh',
        'atanh',
        'cos',
        'cot',
        'csc',
        'sec',
        'sin',
        'tan',
        'cosh',
        'coth',
        'csch',
        'sech',
        'sinh',
        'tanh',
        'exp',
        'ln',
        'log',
        'sqrt',
        'cbrt',
    )
    relational_operators = {
        ast.NotEq: 'Ne',
        ast.Lt: 'Lt',
        ast.LtE: 'Le',
        ast.Gt: 'Gt',
        ast.GtE: 'Ge',
        ast.Eq: 'Eq'
    }

    def visit_Compare(self, node):
        if node.ops[0].__class__ in self.relational_operators:
            sympy_class = self.relational_operators[node.ops[0].__class__]
            right = self.visit(node.comparators[0])
            left = self.visit(node.left)
            new_node = ast.Call(
                func=ast.Name(id=sympy_class, ctx=ast.Load()),
                args=[left, right],
                keywords=[ast.keyword(arg='evaluate', value=ast.Constant(value=False))]
            )
            return new_node
        return node

    def flatten(self, args, func):
        """Рекурсивно расплющивает цепочку вызовов с именем func."""
        result = []
        for arg in args:
            if isinstance(arg, ast.Call):
                arg_func = arg.func
                if isinstance(arg_func, ast.Call):
                    arg_func = arg_func.func
                if hasattr(arg_func, 'id') and arg_func.id == func:
                    result.extend(self.flatten(arg.args, func))
                else:
                    result.append(arg)
            else:
                result.append(arg)
        return result

    def is_division_node(self, node):
        """
        Определяет, является ли узел делением, т.е. имеет вид Mul(числитель, Pow(знаменатель, -1)).
        """
        if (isinstance(node, ast.Call) and hasattr(node.func, 'id') and node.func.id == 'Mul'
                and len(node.args) == 2):
            pow_node = node.args[1]
            if (isinstance(pow_node, ast.Call) and hasattr(pow_node.func, 'id')
                    and pow_node.func.id == 'Pow' and len(pow_node.args) >= 2):
                exp = pow_node.args[1]
                if (isinstance(exp, ast.UnaryOp) and isinstance(exp.op, ast.USub)
                        and isinstance(exp.operand, ast.Constant) and exp.operand.value == 1):
                    return True
        return False

    def extract_division(self, node):
        """
        Извлекает (числитель, знаменатель) из узла вида Mul(числитель, Pow(знаменатель, -1)).
        """
        numerator = node.args[0]
        pow_node = node.args[1]
        denominator = pow_node.args[0]
        return numerator, denominator

    def reassemble_imul_factors(self, factors):
        """
        Перестраивает расплющенную цепочку IMul так, чтобы при встрече делительного узла
        все множители, стоящие после него, шли в знаменателе.

        Например, [2, Mul(2, Pow(IMul(a,b),-1)), c] превращается в узел, соответствующий 2/(a*b*c).
        """
        division_index = None
        for i, factor in enumerate(factors):
            if (isinstance(factor, ast.Call) and hasattr(factor.func, 'id')
                    and factor.func.id == 'Mul' and self.is_division_node(factor)):
                division_index = i
                break
        if division_index is None:
            # Делительного узла нет – возвращаем IMul-узел из всех множителей (если их >1).
            if len(factors) == 1:
                return factors[0]
            return ast.Call(
                func=ast.Name(id='IMul', ctx=ast.Load()),
                args=factors,
                keywords=[ast.keyword(arg='evaluate', value=ast.Constant(value=False))]
            )
        # Если делительный узел найден, то:
        # 1. Факторы до него – в числителе.
        # 2. Из делительного узла извлекаем (num, den).
        # 3. Факторы после него – добавляются к знаменателю.
        before = factors[:division_index]
        div_node = factors[division_index]
        num, den = self.extract_division(div_node)
        numerator_factors = before + [num]
        after = factors[division_index + 1:]
        denominator_factors = [den] + after
        # Собираем числитель:
        if len(numerator_factors) == 1:
            new_num = numerator_factors[0]
        else:
            new_num = ast.Call(
                func=ast.Name(id='IMul', ctx=ast.Load()),
                args=numerator_factors,
                keywords=[ast.keyword(arg='evaluate', value=ast.Constant(value=False))]
            )
        # Собираем знаменатель:
        if len(denominator_factors) == 1:
            new_den = denominator_factors[0]
        else:
            new_den = ast.Call(
                func=ast.Name(id='IMul', ctx=ast.Load()),
                args=denominator_factors,
                keywords=[ast.keyword(arg='evaluate', value=ast.Constant(value=False))]
            )
        # Формируем узел деления: new_num * Pow(new_den, -1)
        new_pow = ast.Call(
            func=ast.Name(id='Pow', ctx=ast.Load()),
            args=[new_den, ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=1))],
            keywords=[ast.keyword(arg='evaluate', value=ast.Constant(value=False))]
        )
        new_div = ast.Call(
            func=ast.Name(id='Mul', ctx=ast.Load()),
            args=[new_num, new_pow],
            keywords=[ast.keyword(arg='evaluate', value=ast.Constant(value=False))]
        )
        return new_div

    def flatten_imul(self, args):
        """
        Сначала расплющивает вложенные IMul, затем пересобирает цепочку, чтобы объединить деление.
        """
        flat = []
        for arg in args:
            if isinstance(arg, ast.Call) and hasattr(arg.func, 'id') and arg.func.id == 'IMul':
                flat.extend(self.flatten(arg.args, 'IMul'))
            else:
                flat.append(arg)
        return self.reassemble_imul_factors(flat)

    def visit_BinOp(self, node):
        if node.op.__class__ in self.operators:
            sympy_class = self.operators[node.op.__class__]
            left = self.visit(node.left)
            right = self.visit(node.right)

            rev = False
            if isinstance(node.op, ast.Sub) or isinstance(node.op, ast.LShift):
                right = ast.Call(
                    func=ast.Name(id='Mul', ctx=ast.Load()),
                    args=[ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=1)), right],
                    keywords=[ast.keyword(arg='evaluate', value=ast.Constant(value=False))]
                )
            elif isinstance(node.op, ast.Div):
                if isinstance(node.left, ast.UnaryOp):
                    left, right = right, left
                    rev = True
                    left = ast.Call(
                        func=ast.Name(id='Pow', ctx=ast.Load()),
                        args=[left, ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=1))],
                        keywords=[ast.keyword(arg='evaluate', value=ast.Constant(value=False))]
                    )
                else:
                    right = ast.Call(
                        func=ast.Name(id='Pow', ctx=ast.Load()),
                        args=[right, ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=1))],
                        keywords=[ast.keyword(arg='evaluate', value=ast.Constant(value=False))]
                    )
            if rev:
                left, right = right, left

            new_node = ast.Call(
                func=ast.Name(id=sympy_class, ctx=ast.Load()),
                args=[left, right],
                keywords=[ast.keyword(arg='evaluate', value=ast.Constant(value=False))]
            )
            if sympy_class in ('Add', 'Mul'):
                new_node.args = self.flatten(new_node.args, sympy_class)
            elif sympy_class == 'IMul':
                new_node = self.flatten_imul(new_node.args)
            return new_node
        return node

    def visit_Call(self, node):
        new_node = self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id in self.functions:
            new_node.keywords.append(
                ast.keyword(arg='evaluate', value=ast.Constant(value=False))
            )
        return new_node


# Объединяем оба трансформера в один, чтобы сначала выполнить преобразование деления, а затем рационализировать цепочки умножения.
class CombinedTransformer(ast.NodeTransformer):
    def __init__(self):
        self.t1 = EvaluateFalseTransformerPatched()
        # self.t2 = EvaluateFalseTransformerPatched()
        # self.t2 = FractionAbsorber()
        # self.t3 = FractionTransformer()

    def visit(self, node):
        node = self.t1.visit(node)
        # node = self.t2.visit(node)
        # node = self.t3.visit(node)
        return node


sympy_parser.EvaluateFalseTransformer = EvaluateFalseTransformerPatched
sympy_parser.EvaluateFalseTransformer = CombinedTransformer
