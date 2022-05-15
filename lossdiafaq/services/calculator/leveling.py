import math
import random
import statistics

def get_stat_modifier(is_attack: bool) -> float:
    return 4.2 if is_attack else 2.1

def rand_stat(base: int) -> int:
    limit: int = min(base, 10000)
    pool_size: int = (limit * (limit + 1) // 2) + limit
    randomized: int = random.randint(0, pool_size)
    stat: int = 0

    if randomized >= limit:
        randomized -= limit
        stat = 1 + int(math.floor((-1 + math.sqrt((8 * randomized) + 1)) // 2))

    return stat

# Returns array:
# [0] = result of this simulation
# [1] = upper bound of stat gain for this
def calc_stat(is_weapon: bool, base: int, is_attack: bool) -> list:
    if base == 0:
        return base

    randomized_result: int = 0
    max_result: int = int(1 + (base // (get_stat_modifier(is_attack) * (2.5 if is_weapon and not is_attack else 1.05))))

    for _ in range(100):
        randomized_result = rand_stat(max_result)

        if randomized_result > 0:
            break

    return [ randomized_result, max_result ]

# Returns array:
# [0] = total stat gained until we reach level_until
# [1] = highest possible stat
# [2] = list of all stat gains (every "gain" is a list)
def simulate_levels(is_weapon: bool, base: int, is_attack: bool, level_until: int = 7) -> list:
    leveling_gains: list = []
    best_possible: int = base

    for _ in range(level_until - 1):
        gain: list = calc_stat(is_weapon, base, is_attack)
        leveling_gains.append(gain)
        base += gain[0]
        best_possible += calc_stat(is_weapon, best_possible, is_attack)[1]

    return [ base, best_possible, leveling_gains ]

# Simulates @simulations times, retrns mean of all results
def get_average(is_weapon: bool, base: int, is_attack: bool, level_until: int = 7, simulations: int = 100) -> int:
    _sum: list = []

    for _ in range(simulations):
        _sum.append(simulate_levels(is_weapon, base, is_attack, level_until)[0])

    return int(statistics.mean(_sum))