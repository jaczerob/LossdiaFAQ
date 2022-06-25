from typing import Optional, Any

import discord

from windiafaq import static


__all__ = ["NormalEmbed", "ErrorEmbed"]


class EmbedField:
    """A wrapper class for :class:`discord.Embed` field values
    
    Attributes
    ----------
    name: :class:`str`
        The name of the field. Can only be up to 256 characters.
    value: :class:`str`
        The value of the field. Can only be up to 1024 characters.
    inline: :class:`bool`
        Whether the field should be displayed inline.
    """

    def __init__(self, *, name: str, value: str, inline: bool = False) -> None:
        self.name = name
        self.value = value
        self.inline = inline


class Embed(discord.Embed):
    """A wrapper class for :class:`discord.Embed`
    Allows for an easier way to add fields to the Embed"""

    def __init__(self, *, color: discord.Color = None, title: Optional[Any] = None, description: Optional[Any] = None):
        super().__init__(color=color, title=title, description=description)

    def add_field(self, embed_field: EmbedField):
        """Adds a field to the embed object
        This function returns the class instance to allow for fluent-style chaining. Can only be up to 25 fields.
        Parameters
        ----------
        embed_field : :class:`EmbedField`
            The field to add to the embed object
        """
        super().add_field(name=embed_field.name, value=embed_field.value, inline=embed_field.inline)


class NormalEmbed(Embed):
    def __init__(self, *, title: Optional[Any] = None, description: Optional[Any] = None, author: Optional[discord.User | discord.Member] = None):
        super().__init__(color=static.BOT_EMBED_COLOR_NORMAL, title=title, description=description)

        if author is not None:
            avatar = author.avatar or author.display_avatar
            self.set_author(name=str(author), icon_url=avatar.url)


class ErrorEmbed(discord.Embed):
    def __init__(self, *, title: Optional[Any] = None, description: Optional[Any] = None):
        super().__init__(color=static.BOT_EMBED_COLOR_ERROR, title=title, description=description)
        