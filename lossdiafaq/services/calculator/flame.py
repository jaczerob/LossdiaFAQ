import math

from lossdiafaq import static


class FlameCalculator:
    def __init__(self, level: int) -> None:
        self.level = level

        self.item_eflame_min_stats = 0
        self.item_eflame_max_stats = 0
        self.item_pflame_min_stats = 0
        self.item_pflame_max_stats = 0

        self.overall_eflame_min_stats = 0
        self.overall_eflame_max_stats = 0
        self.overall_pflame_min_stats = 0
        self.overall_pflame_max_stats = 0

    def calculate(self):
        self.item_eflame_min_stats = (math.floor(self.level / 20) + 1) * static.LOSSDIA_FLAME_EFLAME_MIN_RANGE
        self.item_eflame_max_stats = (math.floor(self.level / 20) + 1) * static.LOSSDIA_FLAME_EFLAME_MAX_RANGE
        self.item_pflame_min_stats = (math.floor(self.level / 20) + 1) * static.LOSSDIA_FLAME_PFLAME_MIN_RANGE
        self.item_pflame_max_stats = (math.floor(self.level / 20) + 1) * static.LOSSDIA_FLAME_PFLAME_MAX_RANGE

        self.overall_eflame_min_stats = (math.floor(self.level / 20) + 1) * static.LOSSDIA_FLAME_EFLAME_MIN_RANGE * 2
        self.overall_eflame_max_stats = (math.floor(self.level / 20) + 1) * static.LOSSDIA_FLAME_EFLAME_MAX_RANGE * 2
        self.overall_pflame_min_stats = (math.floor(self.level / 20) + 1) * static.LOSSDIA_FLAME_PFLAME_MIN_RANGE * 2
        self.overall_pflame_max_stats = (math.floor(self.level / 20) + 1) * static.LOSSDIA_FLAME_PFLAME_MAX_RANGE * 2

        return
