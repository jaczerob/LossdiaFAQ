from difflib import SequenceMatcher
from sqlite3 import OperationalError

from databases import Database


def _is_close_match(command, target):
    return SequenceMatcher(None, command, target).ratio() > min(0.8, 1.0 - 1.0 / len(target))


class FAQDatabase:
    def __init__(self, file_path):
        self._database = Database(file_path)

    async def request(self, command: str):
        if resp := await self._get_description(command):
            return resp

        if closest_matches := await self._get_closest_matches(command):
            return closest_matches

        return None

    async def delete(self, command: str):
        if not self._database.is_connected:
            raise ConnectionError('You are not connected to the Database.')

        if not await self.request(command):
            raise OperationalError(f'{command} does not exist.')

        values = {'command': command}
        query = 'DELETE FROM commands WHERE command = :command;'
        await self._database.execute(query=query, values=values)

    async def update(self, command: str, description: str):
        if not self._database.is_connected:
            raise ConnectionError('You are not connected to the Database.')

        if not await self.request(command):
            raise OperationalError(f'{command} does not exist.')

        values = {'command': command, 'description': description}
        query = 'UPDATE commands SET description = :description WHERE command = :command;'
        await self._database.execute(query=query, values=values)

    async def create(self, command: str, description: str):
        if not self._database.is_connected:
            raise ConnectionError('You are not connected to the Database.')

        if await self.request(command):
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

    async def _get_description(self, command):
        if not self._database.is_connected:
            raise ConnectionError('You are not connected to the Database.')

        values = {'command': command}
        query = 'SELECT description FROM commands WHERE command = :command;'
        resp = await self._database.fetch_one(query=query, values=values)

        if resp:
            return resp['description']
        else:
            return None

    async def _get_closest_matches(self, target):
        if not self._database.is_connected:
            raise ConnectionError('You are not connected to the Database.')

        query = 'SELECT command FROM commands;'
        all_commands = await self._database.fetch_all(query)

        closest_matches = [command for command in all_commands if _is_close_match(command, target)]
        return closest_matches
