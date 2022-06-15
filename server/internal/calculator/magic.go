package calculator

import (
	"errors"
	"fmt"
	"math"
	"strings"

	"github.com/jaczerob/server/internal/utils/static"
)

type Flags struct {
	Flags                       string
	Empty                       bool
	HasAdv, HasDisadv, HasStaff bool
}

func (f *Flags) parse() (err error) {
	f.Empty = f.Flags == ""

	if f.Empty {
		return
	}

	if f.Flags[0] == '-' {
		f.Flags = f.Flags[1:]
	}

	if strings.Contains(f.Flags, " ") {
		return errors.New("Flags cannot contain spaces (ex. -as instead of -a -s)")
	}

	for len(f.Flags) > 0 {
		flag := f.Flags[0]
		f.Flags = f.Flags[1:]

		switch flag {
		case 'e':
			if f.HasDisadv {
				return errors.New("Cannot have both elemental advantage and disadvantage")
			}

			f.HasAdv = true
		case 'd':
			if f.HasAdv {
				return errors.New("Cannot have both elemental advantage and disadvantage")
			}

			f.HasDisadv = true
		case 'l' | 's':
			if f.HasStaff {
				return errors.New("Cannot have two staves")
			}

			f.HasStaff = true
		default:
			return errors.New(fmt.Sprintf("Unknown flag: %b", flag))
		}
	}

	return
}

func ParseFlags(flags string) (f *Flags, err error) {
	f = &Flags{Flags: flags}
	err = f.parse()
	return
}

type MagicCalculator struct {
	HP, SpellAttack             float64
	Flags                       *Flags
	BWMagic, FPILMagic, BSMagic float64
}

func NewMagicCalculator(hp, spellAttack float64, flags string) (m *MagicCalculator, err error) {
	f, err := ParseFlags(flags)
	if err != nil {
		return
	}

	m = &MagicCalculator{
		HP:          hp,
		SpellAttack: spellAttack,
		Flags:       f,
	}

	return
}

func (m *MagicCalculator) Calculate() {
	modifier := m.SpellAttack
	if m.Flags.HasAdv {
		modifier *= static.WindiaMagicElementalAdvantageMultiplier
	} else if m.Flags.HasDisadv {
		modifier *= static.WindiaMagicElementalDisadvantageMultiplier
	}

	if m.Flags.HasStaff {
		modifier *= static.WindiaMagicStaffMultiplier
	}

	m.BWMagic = m.calculateMagic(modifier * static.WindiaMagicBWElementalAmpMultiplier)
	m.FPILMagic = m.calculateMagic(modifier * static.WindiaMagicFPILElementalAmpMultiplier)
	m.BSMagic = m.calculateMagic(modifier)
}

func (m *MagicCalculator) calculateMagic(modifier float64) float64 {
	a := 0.0000333333 * modifier / m.HP
	b := 0.023 * modifier / m.HP
	c := -1.

	root1 := (-1*b + math.Sqrt(b*b-4.*a*c)) / (2 * a)
	root2 := (-1*b - math.Sqrt(b*b-4.*a*c)) / (2 * a)

	return math.Ceil(math.Max(root1, root2))
}
