import sys
import traceback

from discord import errors
from discord.ext import commands
from loguru import logger
import discord

from windiafaq import static
from windiafaq.database.database import FAQDatabase
from windiafaq.discord.context import Context
from windiafaq.discord.embed import ErrorEmbed
from windiafaq.discord import extensions
from windiafaq.ipc.client import IPCClient


def format_traceback(tb: str) -> tuple[str | None, str]:
    """Formats an error traceback to a version easily displayed for Discord
    Wraps the traceback in back ticks to escape all characters
    In case the traceback is over 2,000 characters, it will trim and return the
    full traceback as well
    
    Parameters
    ----------
    tb : :class:`str`
        The error traceback to format
    Returns
    -------
    :class:`tuple`[:class:`str` | :class:`None`, :class:`str`]
        The old traceback, if the traceback is longer than 2,000 characters, and the
        new formatted traceback
    """
    old_tb = None

    if len(tb) > 2000:
        old_tb = tb
        tb = tb[:1990] + '...'
    
    # wrap in back ticks to escape all meme characters
    tb = f"```\n{tb}```"
    return old_tb, tb


class WindiaFAQ(commands.Bot):
    def __init__(self, prefix: str, ipc_endpoint: str) -> None:
        help_command = commands.DefaultHelpCommand(command_attrs=dict(hidden=True))
        super().__init__(prefix, help_command=help_command, owner_id=static.BOT_OWNER_ID, intents=discord.Intents.all(), activity=discord.Game(f"{prefix}help"))
        self.ipc = IPCClient(ipc_endpoint)
        self.db = FAQDatabase()

    async def setup_hook(self) -> None:
        self.ipc.connect()

        for extension in extensions.EXTENSIONS:
            try:
                await self.load_extension(extension)
                logger.info("extension loaded: {}", extension)
            except commands.ExtensionError:
                logger.opt(exception=True).error("could not load extension: {}", extension)

    async def close(self) -> None:
        self.ipc.disconnect()
        return await super().close()

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        return await super().on_message(message)

    async def process_commands(self, message: discord.Message, /) -> None:
        ctx = await self.get_context(message)
        if ctx.command is None:
            return

        await self.invoke(ctx)

    async def get_context(self, origin: discord.Message | discord.Interaction, /, *, cls=Context) -> Context:
        return await super().get_context(origin, cls=cls)

    async def on_error(self, event_method: str, /, *args, **kwargs) -> None:
        if len(args) > 0 and isinstance(args[0], (commands.CommandInvokeError, commands.HybridCommandError, )):
            logger.opt(exception=args[0]).error("error during runtime of {}", event_method)
            tb = "".join(traceback.format_exception(args[0]))
        else:
            exc_info = sys.exc_info()
            if isinstance(exc_info[1], commands.CommandRegistrationError):
                # this is thrown during $commands/aliases add
                # for duplicate FAQ commands to bot commands
                return

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
            # a fatal error within a command that went unchecked
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

