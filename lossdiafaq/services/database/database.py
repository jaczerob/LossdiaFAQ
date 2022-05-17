from typing_extensions import Self
from pymongo.errors import DuplicateKeyError
from pymongo.mongo_client import MongoClient

from lossdiafaq import static
from lossdiafaq.services.database.types import Alias, Command


__all__ = ["FAQDatabase"]


class FAQDatabase:
    def __init__(self):
        self._client = MongoClient(port=static.MONGO_PORT)
        _db = self._client.get_database(static.MONGO_DATABASE)

        self._commands = _db.get_collection(static.MONGO_COLLECTION_COMMANDS)
        self._aliases = _db.get_collection(static.MONGO_COLLECTION_ALIASES)

    def get_all(self) -> list[str]:
        commands_documents = self._commands.find()
        commands = [document["_id"] for document in commands_documents]

        aliases_documents = self._aliases.find()
        aliases = [document["_id"] for document in aliases_documents]
        return commands + aliases

    def get_command(self, command_or_alias: str) -> Command | None:
        document = self._commands.find_one({"_id": command_or_alias})
        if document is None:
            if alias := self.get_alias(command_or_alias):
                document = self._commands.find_one({"_id": alias.command})

        return Command.from_document(document) if document else None

    def add_command(self, command: str, description: str) -> bool:
        cmd = Command(command, description)

        try:
            self._commands.insert_one(cmd.to_document())
            return True
        except DuplicateKeyError:
            return False

    def update_command(self, command: str, description: str) -> bool:
        result = self._commands.update_one({"_id": command}, {"$set": {"description": description}})
        return result.matched_count > 0

    def delete_command(self, command: str) -> bool:
        result = self._commands.delete_one({"_id": command})
        if deleted := result.deleted_count > 0:
            self._aliases.delete_many({"command": command})

        return deleted

    def get_alias(self, alias: str) -> Alias | None:
        document = self._aliases.find_one({"_id": alias})
        return Alias.from_document(document) if document else None

    def add_alias(self, alias: str, command: str) -> bool:
        if not self.get_command(command):
            return False

        al = Alias(alias, command)

        try:
            self._aliases.insert_one(al.to_document())
            return True
        except DuplicateKeyError:
            return False

    def delete_alias(self, alias: str) -> bool:
        result = self._aliases.delete_one({"_id": alias})
        return result.deleted_count > 0
        
    def disconnect(self) -> None:
        return self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_) -> None:
        self.disconnect()
