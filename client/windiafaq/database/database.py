from typing_extensions import Self
from pymongo.errors import DuplicateKeyError
from pymongo.mongo_client import MongoClient

from windiafaq import static
from windiafaq.database.types import Alias, Command


__all__ = ["FAQDatabase"]


class FAQDatabase:
    def __init__(self):
        self._client = MongoClient(port=static.MONGO_PORT, socketTimeoutMS=5)
        _db = self._client.get_database(static.MONGO_DATABASE)

        self._commands = _db.get_collection(static.MONGO_COLLECTION_COMMANDS)
        self._aliases = _db.get_collection(static.MONGO_COLLECTION_ALIASES)

    def get_all(self) -> list[str]:
        """Gets all commands and aliases
        
        Returns
        -------
        :class:`list`[:class:`str`]
            A list of the commands and aliases by their string identifiers, 
            `command` for command and `alias` for alias
        """
        with self._commands.find() as commands_documents:
            commands = [document["_id"] for document in commands_documents if not document.get("hidden", False)]
            commands_documents.close()

            return commands

    def get_command(self, command_or_alias: str) -> Command | None:
        """Gets a command by its name or alias
        
        Parameters
        ----------
        command_or_alias : :class:`str`
            The command or alias of a command to get a command by
        Returns
        -------
        :class:`Command`
            If found, the command object of the command
        :class:`None`
            If the command wasn't found
        """
        document = self._commands.find_one({"_id": command_or_alias})
        if document is None:
            if alias := self.get_alias(command_or_alias):
                document = self._commands.find_one({"_id": alias.command})

        return Command.from_document(document) if document else None

    def add_command(self, command: str, description: str, *, hidden=False) -> bool:
        """Adds a command to the database
        
        Parameters
        ----------
        command : :class:`str`
            The invoke and title of the command
        
        description : :class:`str`
            The return and description of the command
        Returns
        -------
        :class:`bool`
            Whether or not the add was successful    
        """
        if self.get_alias(command):
            # no duplicate keys with aliases
            return False

        cmd = Command(command, description, hidden=hidden)

        try:
            self._commands.insert_one(cmd.to_document())
            return True
        except DuplicateKeyError:
            return False

    def update_command(self, command: str, description: str) -> bool:
        """Updates a command in the database
        
        Parameters
        ----------
        command : :class:`str`
            The invoke and title of the command
        
        description : :class:`str`
            The new return and description of the command
        Returns
        -------
        :class:`bool`
            Whether or not the update was successful    
        """
        result = self._commands.update_one({"_id": command}, {"$set": {"description": description}})
        return result.matched_count > 0

    def delete_command(self, command: str) -> bool:
        """Deletes a command from the database
        
        Parameters
        ----------
        command : :class:`str`
            The invoke and title of the command
        Returns
        -------
        :class:`bool`
            Whether or not the delete was successful    
        """
        result = self._commands.delete_one({"_id": command})
        if deleted := result.deleted_count > 0:
            # delete all aliases associated with the command
            self._aliases.delete_many({"command": command})

        return deleted

    def get_alias(self, alias: str) -> Alias | None:
        """Gets an alias object from the database
        
        Parameters
        ----------
        alias : :class:`str`
            The invoke or title of the alias
        Returns
        -------
        :class:`Alias`
            If found, the alias object of the alias
        :class:`None`
            If the alias wasn't found
        """
        document = self._aliases.find_one({"_id": alias})
        return Alias.from_document(document) if document else None

    def add_alias(self, alias: str, command: str) -> bool:
        """Adds an alias to the database
        
        Parameters
        ----------
        alias : :class:`str`
            The invoke and title of the alias
        
        command : :class:`str`
            The command the alias references
        Returns
        -------
        :class:`bool`
            Whether or not the add was successful    
        """
        if not self.get_command(command):
            # no duplicate keys with commands
            return False

        al = Alias(alias, command)

        try:
            self._aliases.insert_one(al.to_document())
            return True
        except DuplicateKeyError:
            return False

    def delete_alias(self, alias: str) -> bool:
        """Deletes an alias from the database
        
        Parameters
        ----------
        alias : :class:`str`
            The invoke and title of the alias
        Returns
        -------
        :class:`bool`
            Whether or not the delete was successful    
        """
        result = self._aliases.delete_one({"_id": alias})
        return result.deleted_count > 0
        
    def disconnect(self) -> None:
        """Closes database connections"""
        return self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        self.disconnect()