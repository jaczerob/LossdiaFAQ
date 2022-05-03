import random
import sys

import lossdiafaq.static as static


__all__ = ["EESCalculator"]


class EESArgumentError(Exception):
    """Error with EES arguments"""


class EESCalculator:
    def __init__(self, start: int, end: int, delta: int) -> None:
        self.start = start
        self.end = end
        self.delta = delta

        self.avg_attempts = 0
        self.avg_sfprots_used = 0
        self.avg_meso_used = 0
        self.avg_vp_used = 0
        self.avg_dp_used = 0

        self.min_attempts = sys.maxsize
        self.min_sfprots_used = sys.maxsize
        self.min_meso_used = sys.maxsize
        self.min_vp_used = sys.maxsize
        self.min_dp_used = sys.maxsize

        self.max_attempts = -1
        self.max_sfprots_used = -1
        self.max_meso_used = -1
        self.max_vp_used = -1
        self.max_dp_used = -1

    def sample(self):
        if self.start < 0 or self.start > 14:
            raise EESArgumentError("Start must be within 0-14")
            
        if self.end < 1 or self.end > 15:
            raise EESArgumentError("End must be within 1-15")
            
        if self.delta < 0 or self.delta > 4:
            raise EESArgumentError("Protect delta must be within 0-4")

        samples = static.LOSSDIA_EES_SAMPLES
        meso_cost = static.LOSSDIA_EES_MESO_COST
        vp_cost = static.LOSSDIA_EES_SFPROT_VP_COST
        dp_cost = static.LOSSDIA_EES_SFPROT_DP_COST

        for _ in range(samples):
            attempts, sfprots_used = self._attempt_ees()
            meso_used = attempts * meso_cost
            vp_used = sfprots_used * vp_cost
            dp_used = sfprots_used * dp_cost

            self.avg_attempts += attempts / samples
            self.avg_sfprots_used += sfprots_used / samples
            self.avg_meso_used += meso_used / samples
            self.avg_dp_used += dp_used / samples
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

            if dp_used < self.min_dp_used:
                self.min_dp_used = dp_used
            elif dp_used > self.max_dp_used:
                self.max_dp_used = dp_used

            if sfprots_used < self.min_sfprots_used:
                self.min_sfprots_used = sfprots_used
            elif sfprots_used > self.max_sfprots_used:
                self.max_sfprots_used = sfprots_used

        return

    def _enhance(self, level: int) -> tuple[int, bool]:
        rate = max(static.LOSSDIA_EES_MIN_RATE, static.LOSSDIA_EES_BASE_RATE - static.LOSSDIA_EES_REDUCTION_RATE * level)
        random_result = random.random()
        ees_result = random_result < rate

        if level > static.LOSSDIA_EES_MIN_SFPROT_LEVEL:
            sfprot_used = (level % static.LOSSDIA_EES_MIN_SFPROT_LEVEL) >= (static.LOSSDIA_EES_MIN_SFPROT_LEVEL - self.delta)
        else:
            sfprot_used = False

        if ees_result:
            return level + 1, sfprot_used
        elif not ees_result and not sfprot_used:
            return level - 1, sfprot_used
        else:
            return level, sfprot_used

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
    