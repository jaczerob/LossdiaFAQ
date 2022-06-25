package listeners

import (
	"fmt"

	"github.com/jaczerob/server/internal/database"
	"github.com/jaczerob/server/internal/server"
)

type FAQ struct {
	database *database.Database
}

func NewFAQListener() (f *FAQ, err error) {
	database, err := database.NewDatabase()
	if err != nil {
		return
	}

	f = &FAQ{
		database: database,
	}

	return
}

var _ server.CommandListener = (*FAQ)(nil)

func (f *FAQ) Name() string {
	return "faq"
}

func (f *FAQ) Run(c *server.Command) (r *server.ReturnData, err error) {
	var operation string
	if len(c.Args) == 0 {
		operation = ""
	} else {
		operation, err = c.Args.GetString(0)
		if err != nil {
			return
		}
	}

	var out string
	switch operation {
	case "":
		out, err = f.getAllCommands(c)
	case "GetCommand":
		out, err = f.getCommand(c)
	case "AddCommand":
		out, err = f.addCommand(c)
	case "UpdateCommand":
		out, err = f.updateCommand(c)
	case "DeleteCommand":
		out, err = f.deleteCommand(c)
	case "AddAlias":
		out, err = f.addAlias(c)
	}

	if err != nil {
		return
	}

	r = &server.ReturnData{
		Content: out,
	}

	return
}

func (f *FAQ) getAllCommands(c *server.Command) (out string, err error) {
	commands, err := f.database.GetAllCommands()
	if err != nil {
		return "", err
	}

	out = ""
	for _, command := range commands {
		out += command.Command + " "
	}

	return
}

func (f *FAQ) getCommand(c *server.Command) (out string, err error) {
	commandOrAlias, err := c.Args.GetString(1)
	if err != nil {
		return "", err
	}

	command, err := f.database.GetCommand(commandOrAlias)
	if err != nil {
		return "", err
	}

	out = command.Description
	return
}

func (f *FAQ) addCommand(c *server.Command) (out string, err error) {
	command, err := c.Args.GetString(1)
	if err != nil {
		return "", err
	}

	description, err := c.Args.GetString(2)
	if err != nil {
		return "", err
	}

	hidden, err := c.Args.GetBool(3)
	if err != nil {
		return "", err
	}

	err = f.database.AddCommand(command, description, hidden)
	if err != nil {
		return "", err
	}

	out = fmt.Sprintf("%s has been added.", command)
	return
}

func (f *FAQ) updateCommand(c *server.Command) (out string, err error) {
	command, err := c.Args.GetString(1)
	if err != nil {
		return "", err
	}

	description, err := c.Args.GetString(2)
	if err != nil {
		return "", err
	}

	updated, err := f.database.UpdateCommand(command, description)
	if err != nil {
		return "", err
	}

	if updated {
		return fmt.Sprintf("%s has been updated.", command), nil
	} else {
		return fmt.Sprintf("%s has not been updated.", command), nil
	}
}

func (f *FAQ) deleteCommand(c *server.Command) (out string, err error) {
	command, err := c.Args.GetString(1)
	if err != nil {
		return "", err
	}

	deleted, err := f.database.DeleteCommand(command)
	if err != nil {
		return "", err
	}

	if deleted {
		return fmt.Sprintf("%s has been deleted.", command), nil
	} else {
		return fmt.Sprintf("%s has not been deleted.", command), nil
	}
}

func (f *FAQ) addAlias(c *server.Command) (out string, err error) {
	alias, err := c.Args.GetString(1)
	if err != nil {
		return "", err
	}

	command, err := c.Args.GetString(2)
	if err != nil {
		return "", err
	}

	err = f.database.AddAlias(alias, command)
	if err != nil {
		return "", err
	}

	out = fmt.Sprintf("%s has been added.", alias)
	return
}
