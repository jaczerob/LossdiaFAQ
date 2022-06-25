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
	c.ItemEFlameMinStats = c.calculateItem(static.WindiaFlameEFlameMinRange)
	c.ItemEFlameMaxStats = c.calculateItem(static.WindiaFlameEFlameMaxRange)
	c.ItemPFlameMinStats = c.calculateItem(static.WindiaFlamePFlameMinRange)
	c.ItemPFlameMaxStats = c.calculateItem(static.WindiaFlamePFlameMaxRange)

	c.OverallEFlameMinStats = c.calculateOverall(static.WindiaFlameEFlameMinRange)
	c.OverallEFlameMaxStats = c.calculateOverall(static.WindiaFlameEFlameMaxRange)
	c.OverallPFlameMinStats = c.calculateOverall(static.WindiaFlamePFlameMinRange)
	c.OverallPFlameMaxStats = c.calculateOverall(static.WindiaFlamePFlameMaxRange)
}

func (c *FlameCalculator) calculateItem(r float64) float64 {
	return (math.Ceil(c.level/20) + 1) * r
}

func (c *FlameCalculator) calculateOverall(r float64) float64 {
	return (math.Ceil(c.level*static.WindiaFlameOverallMultiplier/20) + 1) * r
}
