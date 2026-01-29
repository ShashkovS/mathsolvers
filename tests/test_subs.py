import pprint
import unittest

import mathsolvers
from mathsolvers.sympy_stuff import tests_wrapper

cases = [
    (r'2x+3', {'?': '1'}),
    (r'\frac{1}{4}*x + 2', {'?': '1'}),
    (r'1 + \frac{1}{4}*x - \frac{1}{2}', {'?': '1'}),
    (r'5,9999999999999 + x', {'?': '1'}),
    (r'x + y + z', {'x': '\\frac{1}{3}', 'z': '4/3'}),
    (r'2x+1/3', {'?': '\\frac{2}{3}'}),
]


class Test(tests_wrapper.TestSolver):
    pass


def add_test_methods():
    for i, (eq, vals) in enumerate(cases):

        def test_subs_with_timeout(self, eq=eq, vals=vals):
            self.maxDiff = None
            res = mathsolvers.subs(eq, vals)
            resa = self.worker.subs(eq, vals)
            pprint.pprint(res, width=120, compact=False, sort_dicts=False)
            self.assertIsNotNone(res)
            self.assertDictEqual(res, resa)

        test_subs_with_timeout.__name__ = tests_wrapper.tnesc(f'test_subs_{i + 1:03}: {eq=} {vals=}')

        setattr(Test, test_subs_with_timeout.__name__, test_subs_with_timeout)


add_test_methods()

if __name__ == '__main__':
    unittest.main()
