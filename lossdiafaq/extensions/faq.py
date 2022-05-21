import re

from discord.ext import commands
import discord
from lossdiafaq import utils

from lossdiafaq.client import LossdiaFAQ
from lossdiafaq.services.discord.embed import NormalEmbed
from lossdiafaq.services.discord.context import Context, FAQContext

class FAQ(commands.Cog):
    def __init__(self, bot: LossdiaFAQ) -> None:
        self.bot = bot
        self.image_url_regex = re.compile(r'^https?:\/\/(?:[a-z0-9\-]+\.)+[a-z]{2,6}(?:\/[^\/#?]+)+\.(?:jpg|gif|png)$')

    async def cog_check(self, ctx: Context) -> bool:
        ctx: FAQContext = await self.bot.get_context(ctx.message, cls=FAQContext)
        return ctx.check

    @commands.hybrid_command(
        name="faq",
        description="displays all FAQ commands",
    )
    async def faq_group(self, ctx: Context):
        """displays all FAQ commands"""
        
        if ctx.interaction:
            await ctx.defer()

        all_commands = sorted(self.bot.db.get_all())
        columns = utils.make_columns(all_commands)

        embed = NormalEmbed(title="FAQ Commands", description=f"```\n{columns}```")
        return await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        ctx: FAQContext = await self.bot.get_context(message, cls=FAQContext)
        if ctx.author.bot:
            return

        command = ctx.get_faq_command()
        if command is None:
            return

        if not ctx.check:
            return await ctx.reply(f"Please use the bot channel, {message.author.mention}.", delete_after=5.0)

        embed = NormalEmbed(title=ctx.faq_command_title, description=command.description, author=ctx.author)

        if match := self.image_url_regex.match(command.description):
            image_url = match.group(0)
            embed.set_image(url=image_url)

        return await ctx.reply(embed=embed)


async def setup(bot: LossdiaFAQ) -> None:
    await bot.add_cog(FAQ(bot))
