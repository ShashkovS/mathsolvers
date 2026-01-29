import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper


class Test(tests_wrapper.TestSolver):
    def test_equivalence(self):
        res = mathsolvers.check_equivalence('x = 8 13/14', 'x = 8\\frac{13}{14}')
        self.assertEqual(True, res['are_equal'])

    def test_strange_linear(self):
        res = mathsolvers.solve('x+1 = 1+x')['final_answer']
        self.assertEqual('$x$ — любое', res)

        res = mathsolvers.solve('x^2+1 = 1+x^2')['final_answer']
        self.assertEqual('$x$ — любое', res)

        res = mathsolvers.solve('x^3+1 = 1+x^3')['final_answer']
        self.assertEqual('$x$ — любое', res)

        res = mathsolvers.solve(r'$\frac{x^{2}-4}{x-2}=0')['final_answer']
        self.assertEqual('$x = -2$', res)

    def test_embed(self):
        res = mathsolvers.embed_solvers(
            r'<<format  $34\%$ \\ dec>>' + '\n'
                                           r'<<format  $122\%$ \\ dec>>' + '\n'
                                                                           r'<<format  $71{,}6\%$ \\ dec>>')
        corr_end = 'final_answer\n$0,34$; $1,22$; $0,716$\n'
        res_end = res[-len(corr_end):]
        self.assertEqual(res_end, corr_end)

    def test_parser(self):
        parsed = mathsolvers.parse(r'$\frac{7^9⋅7^5}{7^12}$')
        self.assertEqual(parsed.simplify(), 49)

        parsed = mathsolvers.parse(r'2^3/4')  # (2³)/4
        self.assertEqual(parsed.simplify(), 2)

        parsed = mathsolvers.parse(r'0,(3)')  # (2³)/4
        self.assertEqual((parsed * 3).simplify(), 1)

        parsed = mathsolvers.parse(r'-0,(3)')  # (2³)/4
        self.assertEqual((parsed * 3).simplify(), -1)

        parsed = mathsolvers.parse(r'12,0(30)')  # (2³)/4
        self.assertEqual((parsed * 33).simplify(), 397)

        res = mathsolvers.solver(r'<<simplify $18^2:27$>>')['final_answer']
        self.assertEqual('$12$', res)

        res = mathsolvers.solver(r'<<simplify $10: \frac{5}{11}$>>')['final_answer']  # был кривой порядок
        self.assertEqual('$22$', res)

    def test_solve(self):
        res = mathsolvers.solve('x^{2}-6 x+8=0')['final_answer']
        self.assertEqual('$x = 2; x = 4$', res)

        res = mathsolvers.solve(r'\frac{x(x - 1)}{2} = 45')['final_answer']
        self.assertEqual('$x = -9; x = 10$', res)

        res = mathsolvers.solver(
            r'<<solve \frac{1}{x} - \frac{1}{y} = 7  \\ \frac{1}{2(x + y)} + \frac{1}{2y} = \frac{1}{x + y} + 4,5 >>'
        )['final_answer']
        self.assertEqual('$x = \\frac{1}{28}, y = \\frac{1}{21} ; x = \\frac{1}{4}, y = -\\frac{1}{3}$', res)

        res = mathsolvers.solver(r'<<solve \frac{5}{7}t = -\frac{25}{28} >>')['final_answer']
        self.assertEqual(r'$t = -\frac{5}{4}$', res)

        res = mathsolvers.solve(r'x + 1 \geq 2')['final_answer']
        self.assertEqual(r'$x \in [1; \infty)$', res)

        res = mathsolvers.solve(r'x+2=\frac{15}{4x+1}')['final_answer']
        self.assertEqual(r'$x = -\frac{13}{4}; x = 1$', res)

        res = mathsolvers.solve(r'$\frac{2 x+16}{x+3}-\frac{1-3 x}{x+3}=0$')['final_answer']
        self.assertEqual(r'Корней нет', res)

        res = mathsolvers.solve(r'$\frac{2\frac{3}{4}}{4\frac{1}{8}}$ = $\frac{1,6}{t}$')['final_answer']
        self.assertEqual(r'$t = 2,4$', res)

        res = mathsolvers.solver(r'<<solve  $\frac {x + 1}{6} + \frac {20}{x - 1} = 4$>>')['final_answer']
        self.assertEqual('$x = 11; x = 13$', res)

        res = mathsolvers.solver(r'<<solve  $\frac{x + 15}{4} - \frac{21}{x + 2} = 2$>>')['final_answer']
        self.assertEqual('$x = -14; x = 5$', res)

        res = mathsolvers.solver(r'<<solve  $\frac{10}{2x-3}$=x-1>>')['final_answer']
        self.assertEqual(r'$x = -1; x = \frac{7}{2}$', res)

        res = mathsolvers.solver(r'<<solve 2,2 - x : 0,3 = 0,13>>')['final_answer']
        self.assertEqual('$x = 0,621$', res)

        res = mathsolvers.solver(r'<<solve (-6) (x + 4) (x - 3) = 0>>')
        self.assertEqual(res['step 1']['answer'], '$(x + 4) (x - 3) = 0$')

    def test_subs(self):
        res = mathsolvers.solver(r'<<simplify x+20=20+x\\x=5>>')['final_answer']
        self.assertEqual('Равенство $x + 20 = 20 + x$ при $x = 5$ выполнено', res)

    def test_factor(self):
        res = mathsolvers.solver(r'<<factor 3+$\sqrt{3}$>>')['final_answer']
        self.assertEqual(r'$3 + \sqrt{3} = 3 + \sqrt{3}$', res)  # TODO "нормальный" factor

    def test_simplify(self):
        res = mathsolvers.solver(r'<<simplify $\sqrt{8,5^{2}-7,5^{2}}$>>')['final_answer']
        self.assertEqual('$4$', res)

        res = mathsolvers.solver(r'<<simplify $a^{-2}: a^{6}$>>')['final_answer']
        self.assertEqual('$\\dfrac{1}{a^{8}}$', res)

        res = mathsolvers.solver(r'<<simplify 608 : 19>>')['final_answer']
        self.assertEqual('$32$', res)

        res = mathsolvers.solver(r'<<simplify | -9,3| >>')['final_answer']
        self.assertEqual('$9,3$', res)

        res = mathsolvers.solver(r'<<simplify 0,009 * 12>>')['final_answer']
        self.assertEqual('$0,108$', res)

        res = mathsolvers.solver(r'<<simplify 1,4 * 2>>')['final_answer']
        self.assertEqual('$2,8$', res)

        res = mathsolvers.solver(r'<<simplify $6^(n+3):6^n$>>')['final_answer']
        self.assertEqual('$216$', res)

        res = mathsolvers.solver(r'<<simplify $\frac{18^n}{2^(n+1) \cdot 3^(2n-1)}>>')['final_answer']
        self.assertEqual(r'$\frac{3}{2}$', res)

        res = mathsolvers.solver(r'<<simplify $\frac{14^(n-1) \cdot 21^(n+1)}{49^n \cdot 6^n }$>>')['final_answer']
        self.assertEqual(r'$\frac{3}{2}$', res)

        res = mathsolvers.solver(r'<<simplify \frac{2^m * 3^{n-1} - 2^{m-1} * 3^n}{2^m * 3^n}>>')['final_answer']
        self.assertEqual(r'$-\frac{1}{6}$', res)

    def test_calc(self):
        res = mathsolvers.solver(r'<<calc 0,4 * 30>>')
        self.assertEqual(str(res) and res.get('answer', ''), r'0,4 \cdot 30 = 12')

        res = mathsolvers.solver(r'<<calc (72 \div 9) + 22>>')
        self.assertEqual(str(res) and res.get('answer', ''), r'(72 \div 9) + 22 = 8 + 22 = 30')

        res = mathsolvers.solver(r'<<calc (3-2) * 5>>')
        self.assertEqual(str(res) and res.get('answer', ''), r'(3 - 2) \cdot 5 = 1 \cdot 5 = 5')


if __name__ == '__main__':
    unittest.main()
