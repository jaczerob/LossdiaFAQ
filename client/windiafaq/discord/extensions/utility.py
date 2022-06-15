from datetime import datetime, timedelta

from dateutil import tz
from discord.ext import commands
import discord.utils

from windiafaq import static
from windiafaq.discord.bot import WindiaFAQ
from windiafaq.discord.command import IPCCommand
from windiafaq.discord.context import Context
from windiafaq.discord.embed import NormalEmbed


class Utility(commands.Cog):
    def __init__(self, bot: WindiaFAQ) -> None:
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.in_dm:
            return True

        if not ctx.in_lossdia or ctx.in_bot_channel:
            return True

        return ctx.is_owner or ctx.is_moderator

    @commands.command(
        name="flame",
        description="shows the flame range for a certain level of gear",
        usage="<item level>",
        aliases=["flames",],
        cls=IPCCommand,
    )
    async def _flame(self, ctx: Context, level: int):
        """shows the flame range for a certain level of gear"""

    @commands.command(
        name="ees",
        description="simulates EES from start to end",
        usage="<start> <end> <protect delta>",
        cls=IPCCommand,
    )
    async def _ees(self, ctx: Context, start: int, end: int, protect_delta: int):
        """simulates EES from start to end
        
        start must be a number between 0 and 14
        end must be a number between 1 and 15
        protect delta must be a number between 0 and 4
        protect delta is the number of stars before a safety point (10, 15) where you will use a SF Prot scroll
        """

    @commands.command(
        name="aees",
        description="simulates AEES from start to end",
        usage="<start> <end> <protect delta>",
        cls=IPCCommand,
    )
    async def _aees(self, ctx: Context, start: int, end: int, protect_delta: int):
        """simulates EES from start to end
        
        start must be a number between 0 and 14
        end must be a number between 1 and 15
        protect delta must be a number between 0 and 4
        protect delta is the number of stars before a safety point (10, 15) where you will use a SF Prot scroll
        """

    @commands.command(
        name="magic",
        description="shows how much magic is needed to one shot a monster with given HP",
        usage="<hp> <spell attack> [<flags>]",
        cls=IPCCommand,
    )
    async def _magic(self, ctx: commands.Context, hp: int, spell_attack: int, flags: str = ""):
        """shows how much magic is needed to one shot a monster with given HP

        flags include (not in any order):
        -l: loveless staff
        -s: elemental staff
        -e: elemental advantage  
        -d: elemental disadvantage

        examples:
        $magic 5000000 670 -l means you are testing against a monster with 5,000,000 HP with a 670 spell attack spell and a Loveless Staff
        """

    @commands.command(
        name="time",
        description="displays the current server time",
    )
    async def _time(self, ctx: Context):
        """displays the current server time"""
        server_time = datetime.utcnow().strftime('%d %b, %Y %H:%M:%S')

        tomorrow = datetime.utcnow() + timedelta(1)
        midnight = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day, hour=0, minute=0, second=0, tzinfo=tz.UTC)

        local_reset_time = discord.utils.format_dt(midnight)
        time_until_reset = discord.utils.format_dt(midnight, style="R")
        
        embed = NormalEmbed(title="Server Time", description=f"The current server time is: {server_time} UTC\nIn your local time, daily reset is at {local_reset_time} ({time_until_reset})", author=ctx.author)
        return await ctx.reply(embed=embed)

    @commands.command(
        name="online",
        description="displays the game's current online count",
    )
    async def _online(self, ctx: Context):
        """displays the game's current online count"""
        if not (lossdia := self.bot.get_guild(static.LOSSDIA_GUILD_ID)):
            return await ctx.reply("I could not get the Lossdia Discord server.")

        lossdia_bot = lossdia.get_member(static.LOSSDIA_BOT_ID)
        if not lossdia_bot or not lossdia_bot.activities:
            return await ctx.reply('I cannot get the online count currently.')

        online_count = lossdia_bot.activities[0].name.split(' ')[3]
        return await ctx.reply(f'Online Users: {online_count}')


async def setup(bot: WindiaFAQ) -> None:
    await bot.add_cog(Utility(bot))
