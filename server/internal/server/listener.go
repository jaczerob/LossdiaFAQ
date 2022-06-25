package server

type CommandListener interface {
	Name() string
	Run(c *Command) (*ReturnData, error)
}
