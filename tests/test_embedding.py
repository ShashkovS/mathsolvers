# flake8: noqa: E501
import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    r"""
<<solve 2x+1=3>>

1
action
Пусть кастрюля стоила $x$ рублей. Сколько рублей стоила сковорода?
solution
Кастрюля стоила на $<<calc 500 - 10 + 20*(1+2)>>$ р. меньше, чем сковорода. Тогда сковорода стоила на 510 р. больше. Получим $x + 510$ р.
answer
$x + 510$ р.

<<solve (x+1)(2x-2) = 0>>

1
action
Пусть кастрюля стоила $x$ рублей. Сколько рублей стоила сковорода?
solution
Кастрюля стоила на $<<calc 500 - 10 + 20*(1+2)>>$ р. меньше, чем сковорода. Тогда сковорода стоила на 510 р. больше. Получим $x + 510$ р.
answer
$x + 510$ р.

final_answer
Сковорода стоила 950 рублей, кастрюля 440 рублей.
""",
    r"""
<<simplify (z + 279) - 99 \\ z = 56>>
<<simplify (z + 279) - 99 \\ z = 75>>
""",
    r"""
<<simplify 1+2>>
<<simplify 2+3>>
вот
""",
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, expr in enumerate(cases):

        def test_embeddings(self, expr=expr):
            txt = mathsolvers.embed_solvers(expr)
            print(txt)

        test_embeddings.__name__ = f'test_embeddings_{i + 1:03}'

        setattr(Test, test_embeddings.__name__, test_embeddings)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
