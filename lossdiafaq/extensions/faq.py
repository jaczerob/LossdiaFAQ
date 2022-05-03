from discord.ext import commands
import discord

from lossdiafaq.client import LossdiaFAQ
from lossdiafaq.services.database.database import Command
from lossdiafaq.services.discord.embed import NormalEmbed
import lossdiafaq.static as static

class FAQCog(commands.Cog):
    def __init__(self, bot: LossdiaFAQ) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="faq",
        description="displays all FAQ commands",
    )
    async def faq_group(self, ctx: commands.Context):
        if ctx.interaction:
            await ctx.defer()

        all_commands = await self.bot.db.get_all()
        all_commands = sorted(all_commands, key=lambda command: command.name)
        longest_command = len(max([command.name for command in all_commands], key=len))
        
        chunked_commands: list[list[Command]] = []
        chunk_size = 3

        for i in range(0, len(all_commands), chunk_size):
            chunked_commands.append(all_commands[i:i+chunk_size])

        fmt = ''
        for commands in chunked_commands:
            line = ''
            for command in commands:
                line += command.name + " " * (longest_command - len(command.name)) + "  "
            
            fmt += line.strip() + "\n"

        embed = NormalEmbed(title="FAQ Commands", description=f"```\n{fmt}```")
        return await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not self.bot.db.is_connected() or message.guild is None:
            return

        if not message.content.startswith(self.bot.command_prefix):
            return

        command = message.content[len(self.bot.command_prefix):]
        if self.bot.get_command(command):
            return

        if message.channel.id != static.LOSSDIA_BOT_CHANNEL_ID and message.guild.id == static.LOSSDIA_GUILD_ID:
            if not self.bot.is_owner(message.author) or not message.channel.permissions_for(message.author).manage_messages:
                return await message.channel.send(f"Please use the bot channel, {message.author.mention}.", delete_after=5.0)

        if not (command := await self.bot.db.get(command)):
            return

        return await message.channel.send(embed=NormalEmbed(title=command.name, description=command.description))


async def setup(bot: LossdiaFAQ) -> None:
    await bot.add_cog(FAQCog(bot))
