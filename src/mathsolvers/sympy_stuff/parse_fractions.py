def _is_valid_expression(expr: str) -> bool:
    stack = []
    for char in expr:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack or stack.pop() != '(':
                return False
    return len(stack) == 0


def _parenthesize(expr: str) -> str:
    expr = expr.strip()
    if (
            expr.isdecimal()
            or expr.isalpha() and len(expr) == 1
            or expr.startswith('(') and expr.endswith(')') and _is_valid_expression(expr[1:-1])
    ):
        return expr
    return f'({expr})'


def convert_fractions(expr: str) -> str:
    """Функция, которая парсит latex-дроби, чтобы не пришлось использовать кривой latex-парсер
    Args:
        expr: строка с выражением

    Returns: строка, в которой дроби замены. Например,
    >>> convert_fractions(r'2 + 1 \\frac{1}{2} + 4')
    '2 + (1 1/2) + 4'
    >>> convert_fractions(r'\\frac{1}{5\\frac{1}{2} + 6 \\frac{1}{3}} + 4')
    '(1/((5 1/2) + (6 1/3))) + 4'
    """
    parts = []
    br_cnt = 0
    ind = 0
    block_start = 0
    frac_parm_num = 0
    is_frac_parm_cmd = False
    frac_parms = []
    last_num_token_start = -1
    mixed_part = ''
    while ind < len(expr):
        c = expr[ind]
        if last_num_token_start < 0 and c.isdecimal():
            last_num_token_start = ind
        if frac_parm_num == 0:
            if c == '\\':
                frac_cmd = None
                if expr[ind + 1: ind + 5] == 'frac':  # frac, dfrac, cfrac, .frac
                    frac_cmd = 5
                elif expr[ind + 2: ind + 6] == 'frac':
                    frac_cmd = 6
                if frac_cmd:
                    # так, у нас дробь! Тут может быть разная дичь... типа \frac12, \frac1{2}, \frac\pi4, \frac\pi{4},
                    frac_parm_num = 1
                    is_frac_parm_cmd = False
                    frac_parms.clear()
                    if last_num_token_start >= 0:
                        # так, у нас тут цепная дробь!
                        mixed_part = expr[last_num_token_start:ind].strip() + ' '
                        parts.append(expr[block_start:last_num_token_start])
                    else:
                        mixed_part = ''
                        parts.append(expr[block_start:ind])
                    ind += frac_cmd
                    block_start = ind
                    ind -= 1  # ещё один +1 в конце цикла
        else:
            # мы парсим дробь.
            if is_frac_parm_cmd and ('a' <= c <= 'z' or 'A' <= c <= 'Z'):
                # Идёт команда-параметр
                pass
            elif is_frac_parm_cmd:
                # параметр был командой, и он закончился
                frac_parms.append(expr[block_start:ind])
                frac_parm_num += 1
                is_frac_parm_cmd = False
                block_start = ind
                ind -= 1  # нужно текущий символ обработать ещё раз, он может быть важным
            elif br_cnt == 0 and c == '\\':
                # параметр может быть командой (типа \pi), тогда может быть без фигурных скобок
                is_frac_parm_cmd = True
            elif br_cnt == 0 and (c.isdecimal() or c.isalpha()):
                # параметр — цифра или переменная
                frac_parms.append(c)
                frac_parm_num += 1
                block_start = ind + 1
            elif c == ' ':
                # Пробелы скипаем
                pass
            elif c == '{' and br_cnt == 0:
                # параметр в фигурных скобках
                br_cnt += 1
                block_start = ind + 1
            elif c == '{':
                # чтоб-то внутри параметра
                br_cnt += 1
            elif c == '}' and br_cnt > 1:
                # чтоб-то внутри параметра
                br_cnt -= 1
            elif c == '}':
                # параметр закончился!
                frac_parms.append(expr[block_start:ind])
                frac_parm_num += 1
                block_start = ind + 1
                br_cnt = 0
            if frac_parm_num > 2:
                p0 = _parenthesize(convert_fractions(frac_parms[0]))
                p1 = _parenthesize(convert_fractions(frac_parms[1]))
                parts.append(f'({mixed_part}{p0}/{p1})')
                frac_parm_num = 0
                frac_parms.clear()
                block_start = ind + 1
        if last_num_token_start >= 0 and not c.isdecimal() and not c.isspace():
            last_num_token_start = -1
        ind += 1
    parts.append(expr[block_start:ind])
    return ''.join(parts)


if __name__ == '__main__':
    print(convert_fractions(r'\frac{a - b}{ac}'))
