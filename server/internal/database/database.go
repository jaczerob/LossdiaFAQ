package database

import (
	"context"

	"github.com/jaczerob/server/internal/utils/static"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type Database struct {
	client   *mongo.Client
	aliases  *mongo.Collection
	commands *mongo.Collection
}

func NewDatabase() (d *Database, err error) {
	client, err := mongo.Connect(context.TODO(), options.Client().ApplyURI(static.MongoDBURI))
	if err != nil {
		return
	}

	windiafaq := client.Database("windiafaq")
	aliases := windiafaq.Collection("aliases")
	commands := windiafaq.Collection("commands")

	d = &Database{
		client:   client,
		aliases:  aliases,
		commands: commands,
	}

	return
}

func (d *Database) Disconnect() error {
	return d.client.Disconnect(context.TODO())
}
