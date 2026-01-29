import re

import mathsolvers
from mathsolvers.solvers_stuff import res_convert

__all__ = ['embed_solvers']

_RE_PARSE = re.compile(r'(?:<<|\[\[)\s*(\w+)\s*\|?\s*(.*?)\s*(?:>>|\]\])', flags=re.DOTALL)
_RE_SPLIT = re.compile(r'\s*\\\\\s*')
_RE_FINAL = re.compile(r'\b[fF]inal_answer:?\s+([\s\S]*?)(?=\s*\n\s*\n|$|(?:"?(?:\d+\s*)[aA]ction))')
_RE_BLOCK_OR_FINAL = re.compile(
    r'\s*"?(\d*)\s*[aA]ction:?\s+([\s\S]*?)\s*'
    r'[sS]olution:?\s+([\s\S]*?)\s*'
    r'[aA]nswer:?\s+([\s\S]*?)(?=\s*\n\s*\n|$|[fF]inal_answer)'
    r'|'
    r'\b[fF]inal_answer:?\s+([\s\S]*?)(?=\s*\n\s*\n|$|(?:"?(?:\d+\s*)[aA]ction))'
)


def _inserter(match: re.Match):
    return res_convert.to_text(mathsolvers.solver(match.group(0)))


fix_formulas_re = re.compile(r'(\${1,2})([^$\n]+?)(\${1,2})')
percent_re = re.compile(r'(?<!\\)%')


def fix_formula(match: re.Match):
    ldol, formula, rdol = match.groups()
    if len(ldol) != len(rdol):
        ldol = rdol = '$$'
    formula = percent_re.sub('\\%', formula)
    return f'{ldol}{formula}{rdol}'


def _embed_calc(text: str) -> str:
    result = []
    in_single_dollar = False
    in_double_dollar = False
    i = 0
    while i < len(text):
        if text[i: i + 2] == '$$':
            in_double_dollar = not in_double_dollar
            result.append('$$')
            i += 2
        elif text[i] == '$' and not in_double_dollar:
            in_single_dollar = not in_single_dollar
            result.append('$')
            i += 1
        elif text[i: i + 7] == '<<calc ' and not in_single_dollar and not in_double_dollar:
            j = i
            while j < len(text) and text[j: j + 2] != '>>':
                j += 1
            j += 2  # To include the closing '>>'
            result.append('$')
            result.append(text[i:j])
            result.append('$')
            i = j
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)


def _solver_calls_counter(match: re.Match, *, cache=set()):
    if match is None:
        cache.clear()
        return None
    tp = match.group(1)
    cache.add(tp)
    if len(cache) <= 1:
        return ''
    return '-'


def embed_solvers(text: str) -> res_convert.SolverStr:
    """embed_solvers — вставить в схему решения результаты вызова алгорешателя.
    Внимание: в итоговом результате только те блоки action/solution/answer, которые парсятся.
    В итоговом результате всегда только последний final_answer
    Args:
        text: схема решения. Если в ней нет блоков action/solution/answer, то результат будет пустым!

    Returns:
    Схема со вставленными решениями алгорешателей

    """
    # Убираем все слеши у процентов (в формулы их вернём)
    text = text.replace('\\%', '%')
    text = fix_formulas_re.sub(fix_formula, text)
    text = '\n'.join(_embed_calc(line) for line in text.splitlines(keepends=False))
    # Есть особый случай: весь текст — это несколько вызовов одинаковых алгорешателей.
    # В этом случае нам нужно склеить final_answer из них всех
    _solver_calls_counter(None)  # сбрасываем кэш
    removed = _RE_PARSE.sub(_solver_calls_counter, text)
    if len(removed.strip(' \n\t0123456789')) == 0:
        join_finals = True
    else:
        join_finals = False
    embedded = _RE_PARSE.sub(_inserter, text)

    all_finals = _RE_FINAL.findall(embedded)
    num_finals = len(all_finals)
    if join_finals and num_finals > 1:
        joined_finals = '; '.join(fin.strip() for fin in all_finals)
        embedded += f'\nfinal_answer\n{joined_finals}\n'
        num_finals += 1
    # Теперь оставляем ровно один последний final_answer
    if num_finals > 1:
        embedded = _RE_FINAL.sub('', embedded, count=num_finals - 1)

    blocks = []
    block_num = 0
    for block in _RE_BLOCK_OR_FINAL.finditer(embedded):
        num, act, sol, ans, fin = block.groups()
        if fin is None:
            block_num += 1
            blocks.append(res_convert._BLOCK_TEMPLATE.format(block_num, act.strip(), sol.strip(), ans.strip()))
        else:
            blocks.append(res_convert._FINAL_ANSWER_TEMPLATE.format(fin.strip()))
    return res_convert.SolverStr('\n'.join(blocks))
