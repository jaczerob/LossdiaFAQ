from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any
from typing_extensions import Self


__all__ = ["Command", "Alias"]


class Documentable(ABC):
    @abstractmethod
    def to_document(self) -> dict[str, str]: ...

    @abstractclassmethod
    def from_document(cls, document: dict[str, Any]) -> Self: ...



class Command(Documentable):
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
