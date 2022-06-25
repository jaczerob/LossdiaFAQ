/*
Credit: Optimist#6397
*/
package calculator

import (
	"errors"
	"math"
	"math/rand"

	"github.com/jaczerob/server/internal/utils/static"
)

type EESCalculator struct {
	Start, End, Delta float64
	baseRate, minRate float64

	AvgAttempts, AvgSFProtsUsed, AvgMesoUsed, AvgVPUsed, AvgCreditsUsed, AvgCOGsUsed, AvgEESUsed float64
	MinAttempts, MinSFProtsUsed, MinMesoUsed, MinVPUsed, MinCreditsUsed, MinCOGsUsed, MinEESUsed float64
	MaxAttempts, MaxSFProtsUsed, MaxMesoUsed, MaxVPUsed, MaxCreditsUsed, MaxCOGsUsed, MaxEESUsed float64
}

func NewEESCalculator(start, end, delta, baseRate, minRate float64) (e *EESCalculator, err error) {
	if start < 0 || start > 14 {
		return nil, errors.New("Start must be within 0-14")
	}

	if end < 1 || end > 15 {
		return nil, errors.New("End must be within 1-15")
	}

	if delta < 0 || delta > 4 {
		return nil, errors.New("Delta must be within 0-4")
	}

	e = &EESCalculator{
		Start:    start,
		End:      end,
		Delta:    delta,
		baseRate: baseRate,
		minRate:  minRate,

		MinAttempts:    math.MaxFloat64,
		MinSFProtsUsed: math.MaxFloat64,
		MinMesoUsed:    math.MaxFloat64,
		MinVPUsed:      math.MaxFloat64,
		MinCreditsUsed: math.MaxFloat64,
		MinCOGsUsed:    math.MaxFloat64,
		MinEESUsed:     math.MaxFloat64,
		MaxAttempts:    -1.,
		MaxSFProtsUsed: -1.,
		MaxMesoUsed:    -1.,
		MaxVPUsed:      -1.,
		MaxCreditsUsed: -1.,
		MaxCOGsUsed:    -1.,
		MaxEESUsed:     -1.,
	}

	return
}

func (e *EESCalculator) Calculate() {
	samples := static.WindiaEESSamples

	for i := 0.; i < samples; i++ {
		attempts, sfProtsUsed := e.attemptEES()
		mesoUsed := attempts * static.WindiaEESMesoCost
		cogsUsed := attempts * static.WindiaAEESCOGCost
		eesUsed := attempts * static.WindiaAEESEESCost
		vpUsed := sfProtsUsed * static.WindiaEESSFProtVPCost
		creditsUsed := sfProtsUsed * static.WindiaEESSFProtCreditsCost

		e.AvgAttempts += attempts / samples
		e.AvgSFProtsUsed += sfProtsUsed / samples
		e.AvgMesoUsed += mesoUsed / samples
		e.AvgVPUsed += vpUsed / samples
		e.AvgCreditsUsed += creditsUsed / samples
		e.AvgCOGsUsed += cogsUsed / samples
		e.AvgEESUsed += eesUsed / samples

		if attempts < e.MinAttempts {
			e.MinAttempts = attempts
		} else if attempts > e.MaxAttempts {
			e.MaxAttempts = attempts
		}

		if mesoUsed < e.MinMesoUsed {
			e.MinMesoUsed = mesoUsed
		} else if mesoUsed > e.MaxMesoUsed {
			e.MaxMesoUsed = mesoUsed
		}

		if vpUsed < e.MinVPUsed {
			e.MinVPUsed = vpUsed
		} else if vpUsed > e.MaxVPUsed {
			e.MaxVPUsed = vpUsed
		}

		if creditsUsed < e.MinCreditsUsed {
			e.MinCreditsUsed = creditsUsed
		} else if creditsUsed > e.MaxCreditsUsed {
			e.MaxCreditsUsed = creditsUsed
		}

		if sfProtsUsed < e.MinSFProtsUsed {
			e.MinSFProtsUsed = sfProtsUsed
		} else if sfProtsUsed > e.MaxSFProtsUsed {
			e.MaxSFProtsUsed = sfProtsUsed
		}

		if cogsUsed < e.MinCOGsUsed {
			e.MinCOGsUsed = cogsUsed
		} else if cogsUsed > e.MaxCOGsUsed {
			e.MaxCOGsUsed = cogsUsed
		}

		if eesUsed < e.MinEESUsed {
			e.MinEESUsed = eesUsed
		} else if eesUsed > e.MaxEESUsed {
			e.MaxEESUsed = eesUsed
		}
	}
}

func (e *EESCalculator) enhance(level float64) (newLevel float64, sfProtUsed bool) {
	rate := math.Ceil(math.Max(e.baseRate-static.WindiaEESReductionRate*level, e.minRate) * 100)
	eesResult := float64(rand.Intn(101)) <= rate

	levelsFromSafepoint := math.Mod(level, 5.)
	sfProtUsed = levelsFromSafepoint >= (5.-e.Delta) && level > 5

	if eesResult {
		newLevel = level + 1
	} else if !eesResult && !sfProtUsed && levelsFromSafepoint != 0 {
		newLevel = level - 1
	} else {
		newLevel = level
	}

	return
}

func (e *EESCalculator) attemptEES() (attempts, sfProtsUsed float64) {
	level := e.Start
	for level < e.End {
		newLevel, sfProtUsed := e.enhance(level)
		attempts += 1.

		if sfProtUsed {
			sfProtsUsed += 1
		}

		level = newLevel
	}

	return
}
