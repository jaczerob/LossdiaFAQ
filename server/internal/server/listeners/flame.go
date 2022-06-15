package listeners

import (
	"fmt"

	"github.com/jaczerob/server/internal/calculator"
	"github.com/jaczerob/server/internal/server"
	"github.com/jaczerob/server/internal/utils"
)

type Flame struct{}

var _ server.CommandListener = (*Flame)(nil)

func (f *Flame) Name() string {
	return "flame"
}

func (f *Flame) Run(c *server.Command) (r *server.ReturnData, err error) {
	level, err := c.Args.GetFloat(0)
	if err != nil {
		return
	}

	flame := calculator.NewFlameCalculator(level)
	flame.Calculate()

	r = &server.ReturnData{
		Embeds: []server.Embed{
			{
				Title:       "Flames Calculator",
				Description: fmt.Sprintf("The flame stats for a level %s item. Overall stats are double that of normal items.", utils.FormatFloat(level)),
				Fields: []server.EmbedField{
					{
						Name:   "Eternal Flame Stat Range",
						Value:  fmt.Sprintf("Overall: %s - %s\nNot Overall: %s - %s", utils.FormatFloat(flame.OverallEFlameMinStats), utils.FormatFloat(flame.OverallEFlameMaxStats), utils.FormatFloat(flame.ItemEFlameMinStats), utils.FormatFloat(flame.ItemEFlameMaxStats)),
						Inline: true,
					},
					{
						Name:   "Powerful Flame Stat Range",
						Value:  fmt.Sprintf("Overall: %s - %s\nNot Overall: %s - %s", utils.FormatFloat(flame.OverallPFlameMinStats), utils.FormatFloat(flame.OverallPFlameMaxStats), utils.FormatFloat(flame.ItemPFlameMinStats), utils.FormatFloat(flame.ItemPFlameMaxStats)),
						Inline: true,
					},
				},
			},
		},
	}
	//		"ItemEFlameMinStats":    flameCalculator.ItemEFlameMinStats,
	//		"ItemEFlameMaxStats":    flameCalculator.ItemEFlameMaxStats,
	//		"ItemPFlameMinStats":    flameCalculator.ItemPFlameMinStats,
	//		"ItemPFlameMaxStats":    flameCalculator.ItemPFlameMaxStats,
	//		"OverallEFlameMinStats": flameCalculator.OverallEFlameMinStats,
	//		"OverallEFlameMaxStats": flameCalculator.OverallEFlameMaxStats,
	//		"OverallPFlameMinStats": flameCalculator.OverallPFlameMinStats,
	//		"OverallPFlameMaxStats": flameCalculator.OverallPFlameMaxStats,
	//	}, nil
	return
}
