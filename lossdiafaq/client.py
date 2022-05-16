from typing import Any
import sys
import traceback

from discord import errors
from discord.ext import commands
from loguru import logger
import discord

from lossdiafaq.services.database.database import FAQDatabase
from lossdiafaq.services.discord.embed import ErrorEmbed
import lossdiafaq.static as static


__all__ = ["LossdiaFAQ"]


def format_traceback(tb: str) -> tuple[str | None, str]:
    old_tb = None

    if len(tb) > 2000:
        old_tb = tb
        tb = tb[:1990] + '...'
    
    tb = f"```\n{tb}```"
    return old_tb, tb


class LossdiaFAQ(commands.Bot):
    def __init__(self, prefix: str) -> None:
        help_command = commands.DefaultHelpCommand(command_attrs=dict(hidden=True))
        super().__init__(prefix, help_command=help_command, intents=discord.Intents.all(), owner_id=static.BOT_OWNER_ID)
        self.db = FAQDatabase(static.DATABASE_URL)

    async def setup_hook(self) -> None:
        for file in static.BOT_EXTENSIONS_PATH.glob("*.py"):
            extension = str(file).replace("/", ".")[:-3]
            if extension.endswith("__init__"):
                continue

            try:
                await self.load_extension(extension, package="lossdiafaq")
                logger.info("extension loaded: {}", extension)
            except commands.ExtensionError:
                logger.opt(exception=True).error("could not load extension: {}", extension)

        await self.db.connect()
        logger.info("database connected to {}", static.DATABASE_URL)

    async def close(self) -> None:
        logger.info("database disconnecting")
        await self.db.disconnect()

        logger.info("bot closing")
        return await super().close()

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        return await super().on_message(message)

    async def on_error(self, event_method: str, /, *args: Any, **kwargs: Any) -> None:
        if len(args) > 0 and isinstance(args[0], (commands.CommandInvokeError, commands.HybridCommandError, )):
            logger.opt(exception=args[0]).error("error during runtime of {}", event_method)
            tb = "".join(traceback.format_exception(args[0]))
        else:
            exc_info = sys.exc_info()
            logger.opt(exception=exc_info).error("error during runtime of {}", event_method)
            
            tb = "".join(traceback.format_exception(exc_info[0], value=exc_info[1], tb=exc_info[2]))

        _, tb = format_traceback(tb)
        
        if channel := self.get_channel(static.BOT_LOGGING_CHANNEL_ID):
            await channel.send(tb)

    async def on_command_error(self, ctx: commands.Context, exception: commands.CommandError, /) -> None:
        if isinstance(exception, (errors.Forbidden, commands.CommandNotFound, )):
            return

        delete_after = None
        if isinstance(exception, (commands.CommandInvokeError, commands.HybridCommandError, )):
            description = "Uh oh >_<"
            await self.on_error(f'command {ctx.invoked_with}', exception)
        elif isinstance(exception, commands.CheckFailure):
            description = "You do not have permissions to use this command!"
            delete_after = 5.0
        elif isinstance(exception, commands.UserInputError):
            description = f"You have misused this command! Here is some help:\n{self.command_prefix}{ctx.command.name} {ctx.command.usage}"
        else:
            exc_type_name = type(exception).__name__
            description = f"Unhandled exception: {exc_type_name}"

        return await ctx.reply(embed=ErrorEmbed(title="Command Error!", description=description), delete_after=delete_after)

