import math

from lossdiafaq import static


class FlameCalculator:
    """A calculator for Flame stats
    
    Attributes
    ----------
    level : :class:`int`
        The level of the gear being tested

    item_eflame_min_stats : :class:`int`
        The minimum range of the eternal flame stats

    item_eflame_max_stats : :class:`int`
        The maximum range of the eternal flame stats

    item_pflame_min_stats : :class:`int`
        The minimum range of the powerful flame stats

    item_pflame_max_stats : :class:`int`
        The maximum range of the powerful flame stats

    overall_eflame_min_stats : :class:`int`
        The minimum range of the eternal flame stats for overalls

    overall_eflame_max_stats : :class:`int`
        The maximum range of the eternal flame stats for overalls

    overall_pflame_min_stats : :class:`int`
        The minimum range of the powerful flame stats for overalls

    overall_pflame_max_stats : :class:`int`
        The maximum range of the powerful flame stats for overalls
    """
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
        """Calculates the stat ranges for each flame and item type
        
        Overalls get double flame stats
        """
        self.item_eflame_min_stats = (math.ceil(self.level / 20) + 1) * static.LOSSDIA_FLAME_EFLAME_MIN_RANGE
        self.item_eflame_max_stats = (math.ceil(self.level / 20) + 1) * static.LOSSDIA_FLAME_EFLAME_MAX_RANGE
        self.item_pflame_min_stats = (math.ceil(self.level / 20) + 1) * static.LOSSDIA_FLAME_PFLAME_MIN_RANGE
        self.item_pflame_max_stats = (math.ceil(self.level / 20) + 1) * static.LOSSDIA_FLAME_PFLAME_MAX_RANGE

        self.overall_eflame_min_stats = self.item_eflame_min_stats * 2
        self.overall_eflame_max_stats = self.item_eflame_max_stats * 2
        self.overall_pflame_min_stats = self.item_pflame_min_stats * 2
        self.overall_pflame_max_stats = self.item_pflame_max_stats * 2

        return
