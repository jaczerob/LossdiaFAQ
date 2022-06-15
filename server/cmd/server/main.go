package main

import (
	"log"
	"os"

	"github.com/jaczerob/server/internal/server"
	"github.com/jaczerob/server/internal/server/listeners"
)

func main() {
	server, err := server.NewServer(os.Getenv("IPC_ENDPOINT"))
	if err != nil {
		log.Fatal(err)
	}

	server.RegisterListener(&listeners.Flame{})
	server.RegisterListener(&listeners.Magic{})
	server.RegisterListener(&listeners.EES{})
	server.RegisterListener(&listeners.AEES{})

	if err = server.Connect(); err != nil {
		log.Fatal(err)
	}

	for {
		if err = server.Listen(); err != nil {
			server.HandleError(err)
		}
	}
}
