package listeners

import (
	"fmt"

	"golang.org/x/text/language"
	"golang.org/x/text/message"

	"github.com/jaczerob/server/internal/calculator"
	"github.com/jaczerob/server/internal/server"
	"github.com/jaczerob/server/internal/utils/static"
)

type AEES struct{}

var _ server.CommandListener = (*AEES)(nil)

func (e *AEES) Name() string {
	return "aees"
}

func (e *AEES) Run(c *server.Command) (r *server.ReturnData, err error) {
	start, err := c.Args.GetFloat(0)
	if err != nil {
		return
	}

	end, err := c.Args.GetFloat(1)
	if err != nil {
		return
	}

	delta, err := c.Args.GetFloat(2)
	if err != nil {
		return
	}

	ees, err := calculator.NewEESCalculator(start, end, delta, static.WindiaAEESBaseRate, static.WindiaAEESMinRate)
	if err != nil {
		return
	}

	ees.Calculate()

	p := message.NewPrinter(language.AmericanEnglish)

	embeds := []server.Embed{
		{
			Title: "AEES Simulator",
			Description: fmt.Sprintf("Took %s AEES on average over %s samples to go from %s* to %s*",
				p.Sprintf("%.2f", ees.AvgAttempts), p.Sprintf("%.0f", static.WindiaEESSamples), p.Sprintf("%.0f", start), p.Sprintf("%.0f", end)),
			Fields: []server.EmbedField{
				{
					Name:   "Stats",
					Value:  "Average AEES Used\nMinimum AEES Used\nMaximum AEES Used\n\nAverage Meso Used\nMinimum Meso Used\nMaximum Meso Used\n\nAverage COGs Used\nMinimum COGs Used\nMaximum COGs Used\n\nAverage EES Used\nMinimum EES Used\nMaximum EES Used",
					Inline: true,
				},
				{
					Name: "Simulated Values",
					Value: fmt.Sprintf("%s\n%s\n%s\n\n%s\n%s\n%s\n\n%s\n%s\n%s\n\n%s\n%s\n%s",
						p.Sprintf("%.2f", ees.AvgAttempts), p.Sprintf("%.0f", ees.MinAttempts), p.Sprintf("%.0f", ees.MaxAttempts), p.Sprintf("%.2f", ees.AvgMesoUsed), p.Sprintf("%.0f", ees.MinMesoUsed), p.Sprintf("%.0f", ees.MaxMesoUsed), p.Sprintf("%.2f", ees.AvgCOGsUsed), p.Sprintf("%.0f", ees.MinCOGsUsed), p.Sprintf("%.0f", ees.MaxCOGsUsed), p.Sprintf("%.2f", ees.AvgEESUsed), p.Sprintf("%.0f", ees.MinEESUsed), p.Sprintf("%.0f", ees.MaxEESUsed)),
					Inline: true,
				},
			},
		},
	}

	if ees.AvgSFProtsUsed > 0. {
		embeds = append(embeds, server.Embed{
			Title: "AEES Simulator",
			Description: fmt.Sprintf("Took %s SF protects on average over %s samples to go from %s* to %s*",
				p.Sprintf("%.2f", ees.AvgSFProtsUsed), p.Sprintf("%.0f", static.WindiaEESSamples), p.Sprintf("%.0f", start), p.Sprintf("%.0f", end)),
			Fields: []server.EmbedField{
				{
					Name:   "Stats",
					Value:  "Average SF Protects Used\nMinimum SF Protects Used\nMaximum SF Protects Used\n\nAverage VP/Credits Used\nMinimum VP/Credits Used\nMaximum VP/Credits Used",
					Inline: true,
				},
				{
					Name: "Simulated Values",
					Value: fmt.Sprintf("%s\n%s\n%s\n\n%s/%s\n%s/%s\n%s/%s",
						p.Sprintf("%.2f", ees.AvgSFProtsUsed), p.Sprintf("%.0f", ees.MinSFProtsUsed), p.Sprintf("%.0f", ees.MaxSFProtsUsed), p.Sprintf("%.2f", ees.AvgVPUsed), p.Sprintf("%.2f", ees.AvgCreditsUsed), p.Sprintf("%.0f", ees.MinVPUsed), p.Sprintf("%.0f", ees.MinCreditsUsed), p.Sprintf("%.0f", ees.MaxVPUsed), p.Sprintf("%.0f", ees.MaxCreditsUsed)),
					Inline: true,
				},
			},
		})
	}

	r = &server.ReturnData{Embeds: embeds}
	return
}
