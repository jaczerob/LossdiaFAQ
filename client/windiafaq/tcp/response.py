import discord

from windiafaq.discord.embed import NormalEmbed, EmbedField


class ServerResponseError(Exception):
    """Raised when the server has encountered an exception handling a command"""


class Response(dict):
    def __init__(self, **kwargs):
        if error := kwargs.pop("error", None):
            raise ServerResponseError(error)
            
        super().__init__(**kwargs)

    def embeds(self) -> list[discord.Embed] | None:
        if not (embeds := self.pop("embeds", None)):
            return None

        _embeds = []

        for embed in embeds:
            _embed = NormalEmbed(title=embed["title"], description=embed["description"])
            if fields := embed.pop("fields"):
                for field in fields:
                    _embed.add_field(EmbedField(name=field["name"], value=field["value"], inline=field["inline"]))

            _embeds.append(_embed)

        return _embeds

    @property
    def content(self) -> str | None:
        return self.pop("content", None)
