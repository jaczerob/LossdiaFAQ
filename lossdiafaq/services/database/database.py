from dataclasses import dataclass
from sqlite3 import OperationalError
from typing import Optional

from databases import Database


__all__ = ["Command", "FAQDatabase"]


@dataclass
class Command:
    name: str
    description: str


class FAQDatabase:
    def __init__(self, file_path):
        self._database = Database(file_path)

    async def get_all(self) -> list[Command]:
        query = 'SELECT * FROM commands;'
        all_commands = [Command(res["command"], res["description"]) for res in await self._database.fetch_all(query)]
        return all_commands

    async def get(self, command: str) -> Optional[Command]:
        if not self._database.is_connected:
            raise ConnectionError('You are not connected to the Database.')

        values = {'command': command}
        query = 'SELECT * FROM commands WHERE command = :command;'
        resp = await self._database.fetch_one(query=query, values=values)

        if resp:
            return Command(resp["command"], resp["description"])
        else:
            return None

    async def delete(self, command: str) -> None:
        if not self._database.is_connected:
            raise ConnectionError('You are not connected to the Database.')

        if not await self.get(command):
            raise OperationalError(f'{command} does not exist.')

        values = {'command': command}
        query = 'DELETE FROM commands WHERE command = :command;'
        await self._database.execute(query=query, values=values)

    async def update(self, command: str, description: str) -> None:
        if not self._database.is_connected:
            raise ConnectionError('You are not connected to the Database.')

        if not await self.get(command):
            raise OperationalError(f'{command} does not exist.')

        values = {'command': command, 'description': description}
        query = 'UPDATE commands SET description = :description WHERE command = :command;'
        await self._database.execute(query=query, values=values)

    async def create(self, command: str, description: str) -> None:
        if not self._database.is_connected:
            raise ConnectionError('You are not connected to the Database.')

        if await self.get(command):
            raise OperationalError(f'{command} already exists.')

        values = {'command': command, 'description': description}
        query = 'INSERT INTO commands(command, description) VALUES(:command, :description);'
        await self._database.execute(query=query, values=values)

    async def connect(self):
        await self._database.connect()

    async def disconnect(self):
        await self._database.disconnect()

    def is_connected(self):
        return self._database.is_connected
