package listeners

import (
	"fmt"

	"github.com/jaczerob/server/internal/calculator"
	"github.com/jaczerob/server/internal/server"
	"github.com/jaczerob/server/internal/utils"
	"github.com/jaczerob/server/internal/utils/static"
)

type Magic struct{}

var _ server.CommandListener = (*Magic)(nil)

func (m *Magic) Name() string {
	return "magic"
}

func (m *Magic) Run(c *server.Command) (r *server.ReturnData, err error) {
	hp, err := c.Args.GetFloat(0)
	if err != nil {
		return
	}

	spellAttack, err := c.Args.GetFloat(1)
	if err != nil {
		return
	}

	flags, err := c.Args.GetString(2)
	if err != nil {
		return
	}

	magic, err := calculator.NewMagicCalculator(hp, spellAttack, flags)
	if err != nil {
		return
	}

	magic.Calculate()

	description := fmt.Sprintf("The magic required to one-shot a monster with %s HP and %s spell attack with modifiers:\n\nBW Elemental Amp: %sx\nFP/IL Elemental Amp: %sx\n",
		utils.FormatFloat(hp), utils.FormatFloat(spellAttack), utils.FormatFloat(static.WindiaMagicBWElementalAmpMultiplier), utils.FormatFloat(static.WindiaMagicFPILElementalAmpMultiplier))

	if magic.Flags.HasAdv {
		description += fmt.Sprintf("Elemental Advantage: %sx\n", utils.FormatFloat(static.WindiaMagicElementalAdvantageMultiplier))
	} else if magic.Flags.HasDisadv {
		description += fmt.Sprintf("Elemental Disadvantage: %sx\n", utils.FormatFloat(static.WindiaMagicElementalDisadvantageMultiplier))
	}

	if magic.Flags.HasStaff {
		description += fmt.Sprintf("Staff Multiplier: %sx\n", utils.FormatFloat(static.WindiaMagicStaffMultiplier))
	}

	r = &server.ReturnData{
		Embeds: []server.Embed{
			{
				Title:       "Magic Calculator",
				Description: description,
				Fields: []server.EmbedField{
					{
						Name:   "Class",
						Value:  "BW\nFP/IL\nBS",
						Inline: true,
					},
					{
						Name:   "Magic",
						Value:  fmt.Sprintf("%s\n%s\n%s", utils.FormatFloat(magic.BWMagic), utils.FormatFloat(magic.FPILMagic), utils.FormatFloat(magic.BSMagic)),
						Inline: true,
					},
				},
			},
		},
	}

	return
}
