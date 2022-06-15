package database

import (
	"context"
	"errors"
	"fmt"

	"go.mongodb.org/mongo-driver/bson"
)

type Alias struct {
	Alias   string `bson:"_id" json:"alias"`
	Command string `bson:"command" json:"command"`
}

func (d *Database) GetAlias(alias string) (a *Alias, err error) {
	result := d.aliases.FindOne(context.TODO(), bson.M{"_id": alias})
	if result.Err() == nil {
		err = result.Decode(&a)
		return
	}

	return nil, nil
}

func (d *Database) AddAlias(alias, command string) (err error) {
	if cmd, _ := d.GetCommand(command); cmd != nil {
		return errors.New(fmt.Sprintf("%s is already a command", alias))
	}

	if al, _ := d.GetAlias(alias); al != nil {
		return errors.New(fmt.Sprintf("%s is already an alias", alias))
	}

	document, err := bson.Marshal(&Alias{Alias: alias, Command: command})
	if err != nil {
		return
	}

	_, err = d.aliases.InsertOne(context.TODO(), document)
	return
}
