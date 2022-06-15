package database

import (
	"context"
	"errors"
	"fmt"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

type Command struct {
	Command     string `bson:"_id" json:"command"`
	Description string `bson:"description" json:"description"`
	Hidden      bool   `bson:"hidden" json:"hidden"`
}

func (d *Database) GetAllCommands() (commands []*Command, err error) {
	results, err := d.commands.Find(context.TODO(), bson.D{})
	if err != nil {
		return
	}

	commands = make([]*Command, 0)
	err = results.All(context.TODO(), commands)
	return
}

func (d *Database) GetCommand(commandOrAlias string) (c *Command, err error) {
	result := d.commands.FindOne(context.TODO(), bson.M{"_id": commandOrAlias})
	if result.Err() == mongo.ErrNoDocuments {
		alias, err := d.GetAlias(commandOrAlias)
		if alias == nil && err != nil {
			return nil, err
		} else if alias == nil {
			return nil, nil
		}

		result = d.commands.FindOne(context.TODO(), bson.M{"_id": alias.Command})
	}

	if result.Err() == nil {
		err = result.Decode(&c)
		return
	}

	return nil, nil
}

func (d *Database) AddCommand(command, description string, hidden bool) (err error) {
	if alias, _ := d.GetAlias(command); alias != nil {
		return errors.New(fmt.Sprintf("%s is already an alias", command))
	}

	if cmd, _ := d.GetAlias(command); cmd != nil {
		return errors.New(fmt.Sprintf("%s is already a command", command))
	}

	document, err := bson.Marshal(&Command{Command: command, Description: description, Hidden: hidden})
	if err != nil {
		return
	}

	_, err = d.commands.InsertOne(context.TODO(), document)
	return
}

func (d *Database) UpdateCommand(command, description string) (bool, error) {
	result, err := d.commands.UpdateByID(context.TODO(), command, bson.M{"$set": bson.M{"description": description}})
	if err != nil {
		return false, err
	}

	return result.MatchedCount > 0, err
}

func (d *Database) DeleteCommand(command string) (bool, error) {
	result, err := d.commands.DeleteOne(context.TODO(), bson.M{"_id": command})
	if err != nil {
		return false, err
	}

	_, err = d.aliases.DeleteMany(context.TODO(), bson.M{"_id": command})
	if err != nil {
		return false, err
	}

	return result.DeletedCount > 0, nil
}
