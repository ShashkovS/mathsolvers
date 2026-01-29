__all__ = ['to_text']
"""
Этот модуль такой изолированный для того, чтобы конвертация не требовала всего mathsolver'а
"""


class SolverStr(str):
    """Класс, предназначенный для отображения результатов работы алгорешателей в jupyter"""

    def __new__(cls, content):
        return str.__new__(cls, content)

    def _repr_markdown_(self):
        # Возвращаем текст как Markdown, что позволит рендерить LaTeX
        return self.replace('\n', '\n\n')


def to_text(sol_obj: dict) -> SolverStr:
    """to_text — Превратить ответ алгорешателя в виде словаря в текстовую схему
    Args:
        sol_obj: словарь с решением, полученный от алгорешателя

    Returns:
    Схема решения в текстовом формате

    """
    if 'final_answer' in sol_obj:
        blocks = []
        for key, val in sol_obj.items():
            if key.startswith('step'):
                blocks.append(_BLOCK_TEMPLATE.format(key[5:], val['action'], val['solution'], val['answer']))
        blocks.append(_FINAL_ANSWER_TEMPLATE.format(sol_obj['final_answer']))
        return SolverStr('\n'.join(blocks))
    if 'answer' in sol_obj:
        return SolverStr(f"${sol_obj['answer']}$")
    return SolverStr('Ошибка алгорешателя: ' + sol_obj.get('error', str(sol_obj)))


_BLOCK_TEMPLATE = """\
{}
action
{}
solution
{}
answer
{}
"""
_FINAL_ANSWER_TEMPLATE = """\

final_answer
{}
"""
