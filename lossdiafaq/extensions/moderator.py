import sqlite3

from discord.ext import commands

from lossdiafaq.client import LossdiaFAQ

class ModeratorCog(commands.Cog):
    def __init__(self, bot: LossdiaFAQ) -> None:
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        if await self.bot.is_owner(ctx.author):
            return True

        if ctx.invoked_subcommand is None:
            return True

        if ctx.guild is None:
            return False

        return ctx.channel.permissions_for(ctx.author).manage_messages

    @commands.command(
        name="add",
        usage="<command> <description>",
        description="adds a FAQ command",
    )
    async def _add(self, ctx: commands.Context, command: str, *, description: str):
        """ex: $add test this is a test"""
        try:
            await self.bot.db.create(command, description)
            return await ctx.send(f"{command} added.")
        except sqlite3.OperationalError:
            return await ctx.send(f"{command} already exists.")

    @commands.command(
        name="update",
        usage="<command> <description>",
        description="updates a FAQ command",
    )
    async def _update(self, ctx: commands.Context, command: str, *, description: str):
        """ex: $update test this is a test updated"""
        try:
            await self.bot.db.update(command, description)
            return await ctx.send(f"{command} updated.")
        except sqlite3.OperationalError:
            return await ctx.send(f"{command} does not exist.")

    @commands.command(
        name="delete",
        usage="<command>",
        description="deletes a FAQ command",
    )
    async def _delete(self, ctx: commands.Context, command: str):
        """ex: $delete test"""
        try:
            await self.bot.db.delete(command)
            return await ctx.send(f"{command} deleted.")
        except sqlite3.OperationalError:
            return await ctx.send(f"{command} does not exist.")


async def setup(bot: LossdiaFAQ) -> None:
    await bot.add_cog(ModeratorCog(bot))
