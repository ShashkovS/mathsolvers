from mathsolvers import strict_compare, check_equivalence

print(strict_compare('2∙⅗ + √179', r'$\sqrt{179} + \frac{3}{5} \cdot 2$'))
# True

print(check_equivalence('2∙⅗ + √179', r'$\sqrt{179} + \frac{3}{5} \cdot 2$'))
# {'expr1': '2∙⅗ + √179', 'expr2': '$\\sqrt{179} + \\frac{3}{5} \\cdot 2$', 'are_equal': True, 'diff': '0'}

print(strict_compare('2(x+1)', '2x + 2'))
# False

print(check_equivalence('2(x+1)', '2x + 2'))
# {'are_equal': True, 'diff': '0', 'expr1': '2(x+1)', 'expr2': '2x + 2'}
