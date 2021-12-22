import math

from sympy import Symbol
from sympy.solvers import solve


def calc_magic(monster_hp: int, modifier: float = 1.0):
    x = Symbol('x')
    mastery = 0.6

    solution = solve(
        ((((x ** 2) / 1000.0 + x * mastery * 0.9) / 30.0 + x / 200.0) * modifier) / monster_hp - 1.0, x
    )

    magic = min([math.ceil(num) for num in solution if num >= 0.0])
    return magic
