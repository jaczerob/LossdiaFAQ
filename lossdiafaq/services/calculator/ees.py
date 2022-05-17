import math
import random
import sys

import lossdiafaq.static as static


__all__ = ["EESCalculator"]


class EESArgumentError(Exception):
    """Error with EES arguments"""


class EESCalculator:
    """Simulates using EES from start to end
    
    Originally written by Optimist#6937
    Modified slightly by jacοb#0828
    
    Attributes
    ----------
    start : :class:`int`

    end : :class:`int`

    delta : :class:`int`

    avg_attempts : :class:`float`
        The average amount of attempts it takes to go from start to end
    
    avg_sfprots_used : :class:`float`
        The average amount of starforce protects it takes to go from start to end

    avg_meso_used : :class:`float`
        The average amount of meso it takes to go from start to end

    avg_vp_used : :class:`float`
        The average amount of VP it takes to go from start to end

    avg_credits_used : :class:`float`
        The average amount of credits it takes to go from start to end

    min_attempts : :class:`float`
        The minimum amount of attempts it took to go from start to end
    
    min_sfprots_used : :class:`float`
        The minimum amount of starforce protects it took to go from start to end

    min_meso_used : :class:`float`
        The minimum amount of meso it took to go from start to end

    min_vp_used : :class:`float`
        The minimum amount of VP it took to go from start to end

    min_credits_used : :class:`float`
        The minimum amount of credits it took to go from start to end

    max_attempts : :class:`float`
        The maximum amount of attempts it took to go from start to end
    
    max_sfprots_used : :class:`float`
        The maximum amount of starforce protects it took to go from start to end

    max_meso_used : :class:`float`
        The maximum amount of meso it took to go from start to end

    max_vp_used : :class:`float`
        The maximum amount of VP it took to go from start to end

    max_credits_used : :class:`float`
        The maximum amount of credits it took to go from start to end
    """
    def __init__(self, start: int, end: int, delta: int) -> None:
        self.start = start
        self.end = end
        self.delta = delta

        self.avg_attempts = 0.
        self.avg_sfprots_used = 0.
        self.avg_meso_used = 0.
        self.avg_vp_used = 0.
        self.avg_credits_used = 0.

        self.min_attempts = sys.maxsize
        self.min_sfprots_used = sys.maxsize
        self.min_meso_used = sys.maxsize
        self.min_vp_used = sys.maxsize
        self.min_credits_used = sys.maxsize

        self.max_attempts = -1
        self.max_sfprots_used = -1
        self.max_meso_used = -1
        self.max_vp_used = -1
        self.max_credits_used = -1

    def simulate(self):
        """Does the EES simulation"""
        if self.start < 0 or self.start > 14:
            raise EESArgumentError("Start must be within 0-14")
            
        if self.end < 1 or self.end > 15:
            raise EESArgumentError("End must be within 1-15")
            
        if self.delta < 0 or self.delta > 4:
            raise EESArgumentError("Protect delta must be within 0-4")

        samples = static.LOSSDIA_EES_SAMPLES
        meso_cost = static.LOSSDIA_EES_MESO_COST
        vp_cost = static.LOSSDIA_EES_SFPROT_VP_COST
        dp_cost = static.LOSSDIA_EES_SFPROT_CREDITS_COST

        for _ in range(samples):
            attempts, sfprots_used = self._attempt_ees()
            meso_used = attempts * meso_cost
            vp_used = sfprots_used * vp_cost
            dp_used = sfprots_used * dp_cost

            self.avg_attempts += attempts / samples
            self.avg_sfprots_used += sfprots_used / samples
            self.avg_meso_used += meso_used / samples
            self.avg_credits_used += dp_used / samples
            self.avg_vp_used += vp_used / samples

            if attempts < self.min_attempts:
                self.min_attempts = attempts
            elif attempts > self.max_attempts:
                self.max_attempts = attempts

            if meso_used < self.min_meso_used:
                self.min_meso_used = meso_used
            elif meso_used > self.max_meso_used:
                self.max_meso_used = meso_used

            if vp_used < self.min_vp_used:
                self.min_vp_used = vp_used
            elif vp_used > self.max_vp_used:
                self.max_vp_used = vp_used

            if dp_used < self.min_credits_used:
                self.min_credits_used = dp_used
            elif dp_used > self.max_credits_used:
                self.max_credits_used = dp_used

            if sfprots_used < self.min_sfprots_used:
                self.min_sfprots_used = sfprots_used
            elif sfprots_used > self.max_sfprots_used:
                self.max_sfprots_used = sfprots_used

        return

    def _enhance(self, level: int) -> tuple[int, bool]:
        rate = math.ceil(max(static.LOSSDIA_EES_BASE_RATE - static.LOSSDIA_EES_REDUCTION_RATE * level, static.LOSSDIA_EES_MIN_RATE) * 100)
        random_result = random.randint(0, 100)
        ees_result = random_result <= rate

        sfprot_used = (level % static.LOSSDIA_EES_MIN_SFPROT_LEVEL) >= (static.LOSSDIA_EES_MIN_SFPROT_LEVEL - self.delta) and level > static.LOSSDIA_EES_MIN_SFPROT_LEVEL

        if not ees_result and level % static.LOSSDIA_EES_MIN_SFPROT_LEVEL == 0:
            # level won't move at safe points (5, 10, 15) if EES fails
            return level, sfprot_used
        elif not ees_result:
            return level - 1 + int(sfprot_used), sfprot_used
        else:
            return level + 1, sfprot_used

    def _attempt_ees(self) -> tuple[int, int]:
        current_level = self.start
        attempts = 0
        sfprots_used = 0
        
        while current_level < self.end:
            current_level, sfprot_used = self._enhance(current_level)
            if sfprot_used:
                sfprots_used += 1
            
            attempts += 1

        return attempts, sfprots_used
    