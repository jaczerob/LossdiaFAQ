from typing import Optional
import math

import lossdiafaq.static as static


__all__ = ["FlagError", "Flags", "MagicCalculator"]


class FlagError(Exception):
    """Error while parsing flags"""


class Flags:
    def __init__(self, flags: Optional[str]) -> None:
        self.flags = flags
        self.empty = True
        self.has_amp = False
        self.has_adv = False
        self.has_disadv = False
        self.has_staff = False

    def parse(self) -> None:
        if self.flags is None:
            return

        if self.flags.startswith("-"):
            self.flags = self.flags[1:]

        if ' ' in self.flags:
            raise FlagError("Flags cannot contain spaces (ex. -as instead of -a -s)")

        self.empty = False

        while len(self.flags) != 0:
            flag = self.flags[0]
            self.flags = self.flags[1:]

            match flag:
                case 'a':
                    self.has_amp = True
                case 'e':
                    if self.has_disadv:
                        raise FlagError("Cannot have both elemental advantage and disadvantage.")

                    self.has_adv = True
                case 'd':
                    if self.has_adv:
                        raise FlagError("Cannot have both elemental advantage and disadvantage.")

                    self.has_disadv = True
                case 'l' | 's':
                    if self.has_staff:
                        raise FlagError("Cannot have two staves.")

                    self.has_staff = True
                case _:
                    raise FlagError(f"unknown flag: {flag}")

        return
    


class MagicCalculator:
    def __init__(self, hp: int, spell_attack: int, flags: Optional[str]) -> None:
        self.hp = hp
        self.spell_attack = spell_attack

        self.flags = Flags(flags)

        self.bw_magic = 0
        self.fpil_magic = 0
        self.bs_magic = 0


    def calculate(self):
        """calculates how much magic is needed to one shot a monster

        Raises
        ------
        FlagError
            error while parsing flags
        """

        self.flags.parse()

        modifier = float(self.spell_attack)
        if self.flags.has_adv:
            modifier *= static.LOSSDIA_MAGIC_ELEMENTAL_ADVANTAGE_MULTIPLIER
        elif self.flags.has_disadv:
            modifier *= static.LOSSDIA_MAGIC_ELEMENTAL_DISADVANTAGE_MULTIPLIER

        if self.flags.has_staff:
            modifier *= static.LOSSDIA_MAGIC_STAFF_MULTIPLIER

        if self.flags.has_amp:
            self.bw_magic = self._calculate_magic(modifier * static.LOSSDIA_MAGIC_BW_ELEMENTAL_AMP_MULTIPLIER)
            self.fpil_magic = self._calculate_magic(modifier * static.LOSSDIA_MAGIC_FPIL_ELEMENTAL_AMP_MULTIPLIER)
        else:
            self.bw_magic = self._calculate_magic(modifier)
            self.fpil_magic = self._calculate_magic(modifier)
            self.bs_magic = self._calculate_magic(modifier)

        return


    def _calculate_magic(self, modifier: float) -> int:
        a = 0.0000333333 * modifier / self.hp
        b = 0.023 * modifier / self.hp
        c = -1.

        root1 = (-1*b + math.sqrt(b*b-4.*a*c)) / (2 * a)
        root2 = (-1*b - math.sqrt(b*b-4.*a*c)) / (2 * a)

        return int(math.ceil(max(root1, root2)))
