from discord import Message
from discord.ext import commands

from windiafaq import static
from windiafaq.database.types import Command


__all__ = ["Context"]


class Context(commands.Context):
    def __init__(self, *, message: Message, bot, **kwargs):
        super().__init__(message=message, bot=bot, **kwargs)

    @property
    def in_dm(self) -> bool:
        return self.guild is None

    @property
    def is_owner(self) -> bool:
        return self.bot.owner_id == self.author.id

    @property
    def in_lossdia(self) -> bool:
        if self.guild is None:
            return False

        return self.guild.id == static.LOSSDIA_GUILD_ID

    @property
    def in_bot_channel(self) -> bool:
        return self.channel.id == static.LOSSDIA_BOT_CHANNEL_ID

    @property
    def is_moderator(self) -> bool:
        if self.guild is None:
            return False

        return self.channel.permissions_for(self.author).manage_messages


class FAQContext(Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.faq_command_title: str = None

    def get_faq_command(self) -> Command | None:
        if not self.message.content.startswith(self.bot.command_prefix):
            return None

        raw_command = self.message.content[len(self.bot.command_prefix):].split(' ')
        self.faq_command_title = command = raw_command[0].lower()
        if self.bot.get_command(command):
            return None
        
        return self.bot.db.get_command(command)

    @property
    def check(self) -> bool:
        if self.in_dm:
            return True

        if not self.in_lossdia or self.in_bot_channel:
            return True

        return self.is_owner or self.is_moderator
