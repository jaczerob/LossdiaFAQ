import re

from discord.ext import commands
import discord

from lossdiafaq import static
from lossdiafaq.client import LossdiaFAQ
from lossdiafaq.services.database.database import Command
from lossdiafaq.services.discord.embed import NormalEmbed

class FAQCog(commands.Cog):
    def __init__(self, bot: LossdiaFAQ) -> None:
        self.bot = bot
        self.image_url_regex = re.compile(r'^https?:\/\/(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:\/[^\/#?]+)+\.(?:jpg|gif|png)$')

    async def cog_check(self, ctx: commands.Context) -> bool:
        if await self.bot.is_owner(ctx.author):
            return True

        if ctx.guild is None:
            return False

        if ctx.channel.id == static.LOSSDIA_BOT_CHANNEL_ID:
            return True

        return ctx.channel.permissions_for(ctx.author).manage_messages

    @commands.hybrid_command(
        name="faq",
        description="displays all FAQ commands",
    )
    async def faq_group(self, ctx: commands.Context):
        """displays all FAQ commands"""
        
        if ctx.interaction:
            await ctx.defer()

        all_commands = sorted(self.bot.db.get_all())
        longest_command = len(max(all_commands, key=len))
        
        chunked_commands: list[list[str]] = []
        chunk_size = 3

        for i in range(0, len(all_commands), chunk_size):
            chunked_commands.append(all_commands[i:i+chunk_size])

        fmt = ''
        for commands in chunked_commands:
            line = ''
            for command in commands:
                line += command + " " * (longest_command - len(command)) + "  "
            
            fmt += line.strip() + "\n"

        embed = NormalEmbed(title="FAQ Commands", description=f"```\n{fmt}```")
        return await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        if not message.content.startswith(self.bot.command_prefix):
            return

        raw_command = message.content[len(self.bot.command_prefix):].split(' ')
        command = title = raw_command[0].lower()
        if self.bot.get_command(command):
            return
        
        if not (command := self.bot.db.get_command(command)):
            return

        if message.channel.id != static.LOSSDIA_BOT_CHANNEL_ID and message.guild.id == static.LOSSDIA_GUILD_ID:
            if not await self.bot.is_owner(message.author) and not message.channel.permissions_for(message.author).manage_messages:
                return await message.channel.send(f"Please use the bot channel, {message.author.mention}.", delete_after=5.0)

        embed = NormalEmbed(title=title, description=command.description, author=message.author)

        if match := self.image_url_regex.match(command.description):
            image_url = match.group(0)
            embed.set_image(url=image_url)

        return await message.channel.send(embed=embed)


async def setup(bot: LossdiaFAQ) -> None:
    await bot.add_cog(FAQCog(bot))
