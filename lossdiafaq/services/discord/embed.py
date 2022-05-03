from typing import Optional, Any

import discord

from lossdiafaq import static


__all__ = ["NormalEmbed", "ErrorEmbed"]


class NormalEmbed(discord.Embed):
    def __init__(self, *, title: Optional[Any] = None, description: Optional[Any] = None, author: Optional[discord.User | discord.Member] = None):
        super().__init__(color=static.BOT_EMBED_COLOR_NORMAL, title=title, description=description)

        if author is not None and author.avatar is not None:
            self.set_author(name=str(author), icon_url=author.avatar.url)

        self.set_footer(text="Ask (DO NOT PING) olivia rodrigo for any suggestions or a moderator if you would like them to $add or $update a FAQ command!")


class ErrorEmbed(discord.Embed):
    def __init__(self, *, title: Optional[Any] = None, description: Optional[Any] = None):
        super().__init__(color=static.BOT_EMBED_COLOR_ERROR, title=title, description=description)
