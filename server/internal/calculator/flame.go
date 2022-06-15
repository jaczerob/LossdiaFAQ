package calculator

import (
	"math"

	"github.com/jaczerob/server/internal/utils/static"
)

type FlameCalculator struct {
	level float64

	ItemEFlameMinStats float64
	ItemEFlameMaxStats float64
	ItemPFlameMinStats float64
	ItemPFlameMaxStats float64

	OverallEFlameMinStats float64
	OverallEFlameMaxStats float64
	OverallPFlameMinStats float64
	OverallPFlameMaxStats float64
}

func NewFlameCalculator(level float64) *FlameCalculator {
	return &FlameCalculator{
		level: level,
	}
}

func (c *FlameCalculator) Calculate() {
	c.ItemEFlameMinStats = (math.Ceil(c.level/20) + 1) * static.WindiaFlameEFlameMinRange
	c.ItemEFlameMaxStats = (math.Ceil(c.level/20) + 1) * static.WindiaFlameEFlameMaxRange
	c.ItemPFlameMinStats = (math.Ceil(c.level/20) + 1) * static.WindiaFlamePFlameMinRange
	c.ItemPFlameMaxStats = (math.Ceil(c.level/20) + 1) * static.WindiaFlamePFlameMaxRange

	c.OverallEFlameMinStats = c.ItemEFlameMinStats * static.WindiaFlameOverallMultiplier
	c.OverallEFlameMaxStats = c.ItemEFlameMaxStats * static.WindiaFlameOverallMultiplier
	c.OverallPFlameMinStats = c.ItemPFlameMinStats * static.WindiaFlameOverallMultiplier
	c.OverallPFlameMaxStats = c.ItemPFlameMaxStats * static.WindiaFlameOverallMultiplier
}
