package server

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"

	"github.com/gookit/event"
	"github.com/pebbe/zmq4"
)

type Server struct {
	endpoint     string
	socket       *zmq4.Socket
	eventManager *event.Manager
}

func NewServer(endpoint string) (s *Server, err error) {
	socket, err := zmq4.NewSocket(zmq4.REP)
	if err != nil {
		return
	}

	s = &Server{
		endpoint:     endpoint,
		socket:       socket,
		eventManager: event.NewManager("Server"),
	}

	return
}

func (s *Server) Connect() (err error) {
	return s.socket.Connect(s.endpoint)
}

func (s *Server) Close() (err error) {
	return s.socket.Close()
}

func (s *Server) Listen() (err error) {
	msg, err := s.socket.Recv(0)
	if err != nil {
		return
	}

	var command *Command
	if err = json.Unmarshal([]byte(msg), &command); err != nil {
		return
	}

	log.SetPrefix(fmt.Sprintf("| %s | ", command.Name()))

	log.Println("received command with args:", command.Args)
	if err = s.HandleCommand(command); err != nil {
		return
	}

	log.Println("marshalling return data")
	data, err := json.Marshal(command.GetReturnData())
	if err != nil {
		return
	}

	log.Println("sending marshalled return data")
	_, err = s.socket.SendBytes(data, zmq4.DONTWAIT)
	return
}

func (s *Server) HandleError(commandError error) {
	errorSend := map[string]string{
		"error": commandError.Error(),
	}

	bytes, err := json.Marshal(&errorSend)
	if err != nil {
		log.Panic(err)
	}

	if _, err = s.socket.SendBytes(bytes, zmq4.DONTWAIT); err != nil {
		log.Panic(err)
	}
}

func (s *Server) HandleCommand(c *Command) error {
	if !s.eventManager.HasListeners(c.Name()) {
		return errors.New(fmt.Sprintf("%s event does not exist", c.Name()))
	}

	return s.eventManager.FireEvent(c)
}

func (s *Server) RegisterListener(listener CommandListener) {
	if s.eventManager.HasListeners(listener.Name()) {
		return
	}

	s.eventManager.AddListener(listener.Name(), event.ListenerFunc(func(e event.Event) error {
		if command, ok := e.(*Command); ok {
			data, err := listener.Run(command)
			if err != nil {
				return err
			}

			command.SetReturnData(data)
			return nil
		}

		return errors.New(fmt.Sprintf("%v is not of type *Command", e))
	}), event.Normal)
}
