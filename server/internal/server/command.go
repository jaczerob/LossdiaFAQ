package server

import (
	"encoding/json"
	"errors"
	"fmt"

	"github.com/gookit/event"
)

type Command struct {
	event.BasicEvent
	CommandName string `json:"command"`
	Args        Args   `json:"args"`
	ReturnData  *ReturnData
}

func (c *Command) Name() string {
	return c.CommandName
}

func (c *Command) SetReturnData(r *ReturnData) {
	c.ReturnData = r
}

func (c *Command) GetReturnData() *ReturnData {
	return c.ReturnData
}

type Args []Arg

func (a Args) get(index int) (arg Arg, err error) {
	if index >= len(a) {
		err = errors.New("index out of bound")
		return
	}

	arg = a[index]
	return
}

func (a Args) GetFloat(index int) (f float64, err error) {
	arg, err := a.get(index)
	if err != nil {
		return
	}

	return arg.AsFloat()
}

func (a Args) GetString(index int) (s string, err error) {
	arg, err := a.get(index)
	if err != nil {
		return
	}

	return arg.AsString()
}

func (a Args) GetBool(index int) (b bool, err error) {
	arg, err := a.get(index)
	if err != nil {
		return
	}

	return arg.AsBool()
}

type Arg struct {
	value interface{}
}

func (a *Arg) UnmarshalJSON(bytes []byte) (err error) {
	var raw interface{}
	if err = json.Unmarshal(bytes, &raw); err != nil {
		return err
	}

	a.value = raw
	return
}

func (a *Arg) AsFloat() (f float64, err error) {
	if f, ok := a.value.(float64); ok {
		return f, nil
	}

	err = errors.New(fmt.Sprintf("%v is not a float", a.value))
	return
}

func (a *Arg) AsString() (s string, err error) {
	if s, ok := a.value.(string); ok {
		return s, nil
	}

	err = errors.New(fmt.Sprintf("%v is not a string", a.value))
	return
}

func (a *Arg) AsBool() (b bool, err error) {
	if b, ok := a.value.(bool); ok {
		return b, nil
	}

	err = errors.New(fmt.Sprintf("%v is not a bool", a.value))
	return
}
