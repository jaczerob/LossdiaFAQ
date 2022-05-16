from typing import Optional, Any

import discord

from lossdiafaq import static


__all__ = ["NormalEmbed", "ErrorEmbed"]


class EmbedField:
    def __init__(self, *, name: str, value: str, inline: bool = False) -> None:
        self.name = name
        self.value = value
        self.inline = inline


class Embed(discord.Embed):
    def __init__(self, *, color: discord.Color = None, title: Optional[Any] = None, description: Optional[Any] = None):
        super().__init__(color=color, title=title, description=description)

    def add_field(self, embed_field: EmbedField):
        super().add_field(name=embed_field.name, value=embed_field.value, inline=embed_field.inline)


class NormalEmbed(Embed):
    def __init__(self, *, title: Optional[Any] = None, description: Optional[Any] = None, author: Optional[discord.User | discord.Member] = None):
        super().__init__(color=static.BOT_EMBED_COLOR_NORMAL, title=title, description=description)

        if author is not None:
            avatar = author.avatar or author.display_avatar
            self.set_author(name=str(author), icon_url=avatar.url)

        self.set_footer(text="Ask (DO NOT PING) olivia rodrigo for any suggestions or a moderator if you would like them to $add or $update a FAQ command!")


class ErrorEmbed(discord.Embed):
    def __init__(self, *, title: Optional[Any] = None, description: Optional[Any] = None):
        super().__init__(color=static.BOT_EMBED_COLOR_ERROR, title=title, description=description)
