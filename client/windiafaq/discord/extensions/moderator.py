from discord.ext import commands

from windiafaq.discord.bot import WindiaFAQ
from windiafaq.discord.embed import ErrorEmbed
from windiafaq.discord.context import Context


class Moderator(commands.Cog):
    def __init__(self, bot: WindiaFAQ) -> None:
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.in_dm:
            return False

        return ctx.is_owner or ctx.is_moderator

    async def cog_before_invoke(self, ctx: Context) -> None:
        for arg in ctx.args[2:]:
            if self.bot.get_command(arg):
                await ctx.reply(embed=ErrorEmbed(title="Command Error!", description=f"The command {arg} already exists!"))
                raise commands.CommandRegistrationError(arg)

    @commands.group(
        name="commands",
        description="a group to manage FAQ commands and aliases",
    )
    async def _commands(self, ctx: Context):
        """FAQ command manager
        To add a command, $commands add <command> <description>
        To update a command, $commands update <command> <description>
        To delete a command, $commands delete <command>
        """

        if ctx.invoked_subcommand:
            return

        return await ctx.send_help(ctx.command)

    @_commands.command(
        name="add",
        usage="<command> <description>",
        description="adds a FAQ command",
    )
    async def _commands_add(self, ctx: Context, command: str, *, description: str):
        """ex: $commands add example this is an example"""

        if self.bot.db.add_command(command, description):
            return await ctx.reply(f"{command} added.")
        else:
            return await ctx.reply(f"{command} was not added.")

    @_commands.command(
        name="add_special",
        usage="<command> <description>",
        description="adds a special FAQ command",
    )
    async def _commands_add_special(self, ctx: Context, command: str, *, description: str):
        """ex: $commands add example this is an example"""

        if self.bot.db.add_command(command, description, hidden=True):
            return await ctx.reply(f"{command} added.")
        else:
            return await ctx.reply(f"{command} was not added.")

    @_commands.command(
        name="update",
        usage="<command> <description>",
        description="updates a FAQ command",
    )
    async def _commands_update(self, ctx: Context, command: str, *, description: str):
        """ex: $commands update example this is an example updated"""

        if self.bot.db.update_command(command, description):
            return await ctx.reply(f"{command} updated.")
        else:
            return await ctx.reply(f"{command} was not updated.")

    @_commands.command(
        name="delete",
        usage="<command>",
        description="deletes a FAQ command",
    )
    async def _commands_delete(self, ctx: Context, command: str):
        """ex: $commands delete example"""

        if self.bot.db.delete_command(command):
            return await ctx.reply(f"{command} deleted.")
        else:
            return await ctx.reply(f"{command} was not deleted.")

    @commands.group(
        name="aliases",
        description="a group to manage FAQ aliases and aliases",
    )
    async def _aliases(self, ctx: Context):
        """FAQ alias manager
        To add an alias, $aliases add <alias> <command>
        To delete an alias, $aliases delete <alias>
        """

        if ctx.invoked_subcommand:
            return

        return await ctx.send_help(ctx.command)

    @_aliases.command(
        name="add",
        usage="<alias> <command>",
        description="adds a FAQ alias",
    )
    async def _alias_add(self, ctx: Context, alias: str, command: str):
        """ex: $aliases add example_alias example_command"""

        if self.bot.db.add_alias(alias, command):
            return await ctx.reply(f"{alias} added.")
        else:
            return await ctx.reply(f"{alias} was not added.")

    @_aliases.command(
        name="delete",
        usage="<alias>",
        description="deletes a FAQ alias",
    )
    async def _alias_delete(self, ctx: Context, alias: str):
        """ex: $aliases delete example_alias"""

        if self.bot.db.delete_alias(alias):
            return await ctx.reply(f"{alias} deleted.")
        else:
            return await ctx.reply(f"{alias} was not deleted.")


async def setup(bot: WindiaFAQ) -> None:
    await bot.add_cog(Moderator(bot))