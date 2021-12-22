import argparse
import math
import random


def parse_args():
    parser = argparse.ArgumentParser("Simulate EES scrolling.")
    parser.add_argument("ees")
    parser.add_argument("--protect-delta", dest="protect_delta", type=int, default=0)
    parser.add_argument("--samples", type=int, default=10000)
    return parser.parse_args()


def enhance(level, protect_delta):
    base_rate = 0.75
    rate_reduction = level * 0.05
    rate = math.ceil(max(base_rate - rate_reduction, 0.10) * 100)

    rand_result = random.randint(0, 100)
    ees_result = rand_result <= rate

    sfprot_used = int((level % 5) >= (5 - protect_delta) and level > 5)
    if not ees_result and level % 5 == 0:
        return (level, sfprot_used)

    if not ees_result:
        return (level - 1 + sfprot_used, sfprot_used)

    return (level + 1, sfprot_used)


def attempt_ees(start, end, protect_delta):
    attempts = 0
    sfprot_used = 0
    level = start
    while level < end:
        level, sfprot = enhance(level, protect_delta)
        attempts += 1
        sfprot_used += sfprot
    return (attempts, sfprot_used)


def sample(ees, protect_delta, samples):
    results = []
    start, end = map(int, ees.split('-'))
    for i in range(samples):
        results.append(attempt_ees(start, end, protect_delta))

    avg = sum([r[0] for r in results]) / len([r[0] for r in results])
    sfavg = sum([r[1] for r in results]) / len([r[1] for r in results])
    _min = min([r[0] for r in results])
    sf_min = min([r[1] for r in results])
    _max = max([r[0] for r in results])
    sf_max = max([r[1] for r in results])

    return {
        'ees_average': avg,
        'ees_min': _min,
        'ees_max': _max,
        'sfprot_average': sfavg,
        'sfprot_min': sf_min,
        'sfprot_max': sf_max,
        'description': f"Took {avg:,.2f} EES w/ {sfavg:,.2f} SF protects on average over {samples:,} samples to go from {start}* to {end}*.",
    }


if __name__ == '__main__':
    args = parse_args()
    print(sample(args.ees, args.protect_delta, args.samples).get('description'))
