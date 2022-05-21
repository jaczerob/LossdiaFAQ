from collections import OrderedDict
from discord.ext import commands
import discord.utils
import discord

from lossdiafaq.client import LossdiaFAQ
from lossdiafaq.services.discord.embed import NormalEmbed, EmbedField
from lossdiafaq.services.discord.context import Context

class User(commands.Cog):
    def __init__(self, bot: LossdiaFAQ) -> None:
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.in_dm:
            return False

        if not ctx.in_lossdia or ctx.in_bot_channel:
            return True

        return ctx.is_owner or ctx.is_moderator

    @commands.hybrid_command(
        name="user",
        description="shows your user info",
    )
    async def _user(self, ctx: Context):
        """shows your user info"""
        top_role_fmt = f" ({ctx.author.top_role.mention})" if ctx.author.top_role != ctx.guild.default_role else ""

        embed = NormalEmbed(
            title=f"{ctx.author}'s user info",
            author=ctx.author,
        )

        created_at = discord.utils.format_dt(ctx.author.created_at)
        created_at_relative = discord.utils.format_dt(ctx.author.created_at, style="R")

        general_information_field = EmbedField(name="ℹ️ General Information", value="")
        general_information_field.value += f"User: {ctx.author.mention}{top_role_fmt}\n"
        general_information_field.value += f"Joined Discord at {created_at} ({created_at_relative})"

        embed.add_field(general_information_field)

        joined_at = discord.utils.format_dt(ctx.author.joined_at)
        joined_at_relative = discord.utils.format_dt(ctx.author.joined_at, style="R")

        join_position = sorted(ctx.guild.members, key=lambda member: member.created_at).index(ctx.author) + 1

        guild_information_field = EmbedField(name="ℹ️ Guild Information", value="")
        guild_information_field.value += f"Nickname: {ctx.author.nick}\n" if ctx.author.nick else ""
        guild_information_field.value += f"Joined {ctx.guild} at {joined_at} ({joined_at_relative})\n"
        guild_information_field.value += f"Join position: {join_position}/{ctx.guild.member_count}"

        if ctx.author.premium_since:
            boosted_since = discord.utils.format_dt(ctx.author.premium_since)
            boosted_since_relative = discord.utils.format_dt(ctx.author.premium_since, style="R")
            guild_information_field.value += f"💎 🥶 Boosted {ctx.guild} since {boosted_since} ({boosted_since_relative})"

        embed.add_field(guild_information_field)
        return await ctx.reply(embed=embed)


async def setup(bot: LossdiaFAQ) -> None:
    await bot.add_cog(User(bot))
