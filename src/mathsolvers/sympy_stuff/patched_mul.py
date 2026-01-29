import sympy

__all__ = ['IMul']

IMul = sympy.Mul

# Это всё нужно для патча, который парсит
# 2/ab как 2/(ab)
