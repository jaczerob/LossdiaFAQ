from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any
from typing_extensions import Self


__all__ = ["Command", "Alias"]


class Documentable(ABC):
    """An abstract class to frame a class to be transferrable from and to Mongo documents"""
    @abstractmethod
    def to_document(self) -> dict[str, str]: 
        """Converts the class to a Mongo document
        
        Returns
        -------
        :class:`dict`[:class:`str`, :class:`str`]
            A mapping of the class's attributes in the form of a Mongo document
        """

    @abstractclassmethod
    def from_document(cls, document: dict[str, Any]) -> Self:
        """Creates this object using a Mongo document

        Parameters
        ----------
        document : :class:`dict`[:class:`str`, :class:`Any`]
            The Mongo document obtained from a database

        Returns
        -------
        :class:`Self`
            This object as a representation of a Mongo document
        """


class Command(Documentable):
    """An object representing a FAQ command
    
    Attributes
    ----------
    command : :class:`str`
        The invoke or title of the command
        
    description : :class:`str`
        The return or description of the command
    """
    def __init__(self, command: str, description: str) -> None:
        self.command = command
        self.description = description

    def to_document(self):
        return {
            '_id': self.command,
            'description': self.description,
        }

    @classmethod
    def from_document(cls: Self, document: dict[str, Any]) -> Self:
        return cls(document["_id"], document["description"])


class Alias(Documentable):
    """An object representing a FAQ alias
    
    Attributes
    ----------
    alias : :class:`str`
        The invoke or title of the alias
        
    command : :class:`str`
        The command the alias is representing
    """
    def __init__(self, alias: str, command: str) -> None:
        self.alias = alias
        self.command = command

    def to_document(self):
        return {
            '_id': self.alias,
            'command': self.command,
        }

    @classmethod
    def from_document(cls: Self, document: dict[str, Any]) -> Self:
        return cls(document["_id"], document["command"])
