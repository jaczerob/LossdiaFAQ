from datetime import datetime, timedelta
from typing import Optional

from discord.ext import commands
import discord

from lossdiafaq import static
from lossdiafaq.client import LossdiaFAQ
from lossdiafaq.services.calculator.ees import EESArgumentError, EESCalculator
from lossdiafaq.services.calculator.flame import FlameCalculator
from lossdiafaq.services.calculator.magic import FlagError, MagicCalculator
from lossdiafaq.services.discord import NormalEmbed
from lossdiafaq.services.discord.embed import ErrorEmbed


class Utility(commands.Cog):
    def __init__(self, bot: LossdiaFAQ) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="magic",
        description="shows how much magic is needed to one shot a monster with given HP",
        usage="<hp> <spell attack> [<flags>]",
    )
    async def _magic(self, ctx: commands.Context, hp: int, spell_attack: int, flags: Optional[str]):
        """shows how much magic is needed to one shot a monster with given HP

        flags include (not in any order):
        -l: loveless staff
        -s: elemental staff
        -e: elemental advantage  
        -d: elemental disadvantage
        -a: elemental amp

        ex: $magic x x -al means you are testing with elemental amp and loveless staff
        """

        if ctx.interaction is not None:
            await ctx.defer()

        magic = MagicCalculator(hp, spell_attack, flags)
        try:
            magic.calculate()
        except FlagError as error:
            return await ctx.send(embed=ErrorEmbed(
                title="Flag Error",
                description=str(error),
            ))

        magic_embed = NormalEmbed(
            title="Magic Calculator",
            description=f"The magic required to one shot a monster with {hp} HP with {spell_attack} spell attack",
            author=ctx.author,
        )

        modifier_label_field = {
            "name": "Modifier",
            "value": "",
            "inline": True,
        }

        modifier_value_field = {
            "name": "Multiplier",
            "value": "",
            "inline": True,
        }

        if magic.flags.has_amp:
            modifier_label_field["value"] += "BW Elemental Amplification\n"
            modifier_value_field["value"] += "{:.02f}\n".format(static.LOSSDIA_MAGIC_BW_ELEMENTAL_AMP_MULTIPLIER)

            modifier_label_field["value"] += "FP/IL Elemental Amplification\n"
            modifier_value_field["value"] += "{:.02f}\n".format(static.LOSSDIA_MAGIC_FPIL_ELEMENTAL_AMP_MULTIPLIER)
        
        if magic.flags.has_adv:
            modifier_label_field["value"] += "Elemental Advantage\n"
            modifier_value_field["value"] += "{:.02f}\n".format(static.LOSSDIA_MAGIC_ELEMENTAL_ADVANTAGE_MULTIPLIER)
        
        if magic.flags.has_disadv:
            modifier_label_field["value"] += "Elemental Disadvantage\n"
            modifier_value_field["value"] += "{:.02f}\n".format(static.LOSSDIA_MAGIC_ELEMENTAL_DISADVANTAGE_MULTIPLIER)
        
        if magic.flags.has_staff:
            modifier_label_field["value"] += "Staff Multiplier\n"
            modifier_value_field["value"] += "{:.02f}\n".format(static.LOSSDIA_MAGIC_STAFF_MULTIPLIER)

        """
        if modifier_label_field["value"] != "" and modifier_value_field["value"] != "":
            magic_embed.add_field(**modifier_label_field)
            magic_embed.add_field(**modifier_value_field)
        """
        
        class_field = {
            "name": "Class",
            "value": "BW\nI/L\nF/P\n",
            "inline": True,
        }

        magic_field = {
            "name": "Magic",
            "value": "{:,}\n{:,}\n{:,}\n".format(magic.bw_magic, magic.fpil_magic, magic.fpil_magic),
            "inline": True,
        }

        if not magic.flags.has_amp:
            class_field["value"] += "BS"
            magic_field["value"] += "{:,}".format(magic.bs_magic)

        magic_embed.add_field(**class_field)
        magic_embed.add_field(**magic_field)
        return await ctx.send(embed=magic_embed)

    @commands.hybrid_command(
        name="time",
        description="displays the current server time",
    )
    async def _time(self, ctx: commands.Context):
        """displays the current server time"""
        time = datetime.utcnow().strftime('%d %b, %Y %H:%M:%S')

        tomorrow = datetime.utcnow() + timedelta(1)
        midnight = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day,
                            hour=0, minute=0, second=0)
        reset_delta = (midnight - datetime.utcnow())
        time_until_reset = str(reset_delta).split('.')[0]
        
        embed = NormalEmbed(title="Server Time", description=f"The current server time is: {time}\nTime until reset: {time_until_reset}", author=ctx.author)
        return await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="online",
        description="displays the game's current online count",
    )
    async def _online(self, ctx: commands.Context):
        """displays the game's current online count"""
        if not (lossdia := self.bot.get_guild(static.LOSSDIA_GUILD_ID)):
            return await ctx.send("I could not get the Lossdia Discord server.")

        lossdia_bot = lossdia.get_member(static.LOSSDIA_BOT_ID)
        if not lossdia_bot or not lossdia_bot.activities:
            return await ctx.send('I cannot get the online count currently.')

        online_count = lossdia_bot.activities[0].name.split(' ')[3]
        return await ctx.send(f'Online Users: {online_count}')

    @commands.hybrid_command(
        name="flame",
        description="shows the flame range for a certain level of gear",
        usage="<item level>",
        aliases=["flames",]
    )
    async def _flame(self, ctx: commands.Context, level: int):
        """shows the flame range for a certain level of gear"""

        flames = FlameCalculator(level)
        flames.calculate()

        flames_embed = NormalEmbed(
            title="Flames Calculator",
            description="",
            author=ctx.author,
        )

        eflame_field = {
            "name": "Eternal Flame Stat Range",
            "value": "Overall: {} - {}\nNot Overall: {} - {}".format(flames.overall_eflame_min_stats, flames.overall_eflame_max_stats, flames.item_eflame_min_stats, flames.item_eflame_max_stats),
            "inline": False,
        }

        pflame_field = {
            "name": "Powerful Flame Stat Range",
            "value": "Overall: {} - {}\nNot Overall: {} - {}".format(flames.overall_pflame_min_stats, flames.overall_pflame_max_stats, flames.item_pflame_min_stats, flames.item_pflame_max_stats),
            "inline": False,
        }

        flames_embed.add_field(**eflame_field)
        flames_embed.add_field(**pflame_field)
        return await ctx.send(embed=flames_embed)


    @commands.hybrid_command(
        name="ees",
        description="simulates EES from start to end",
        usage="<start> <end> <protect delta>",
    )
    async def _ees(self, ctx: commands.Context, start: int, end: int, protect_delta: int):
        """simulates EES from start to end
        
        start must be a number between 0 and 14
        end must be a number between 1 and 15
        protect delta must be a number between 0 and 4

        protect delta is the number of stars before a safety point (10, 15) where you will use a SF Prot scroll
        """

        if ctx.interaction is not None:
            await ctx.defer()

        ees = EESCalculator(start, end, protect_delta)

        message = await ctx.send(f'Running simulation of EES from {start}* to {end}* {static.LOSSDIA_EES_SAMPLES} times...')
        
        try:
            await self.bot.loop.run_in_executor(None, ees.sample)
        except EESArgumentError as error:
            await message.delete()
            return await ctx.send(embed=ErrorEmbed(
                title="EES Simulator Argument Error",
                description=str(error),
            ))

        await message.delete()

        ees_embed = discord.Embed(
            color=static.BOT_EMBED_COLOR_NORMAL,
            title="EES Simulator",
            description="Took {:,.02f} EES on average over {:,} samples to go from {}* to {}*".format(ees.avg_attempts, static.LOSSDIA_EES_SAMPLES, start, end),
        )

        ees_label_field = {
            "name":   "Stats",
            "value":  "Average Used\nMinimum Used\nMaximum Used\nAverage Meso Used\nMinimum Meso Used\nMaximum Meso Used",
            "inline": True,
        }

        ees_value_field_description = "{:,.02f}\n{:,}\n{:,}\n{:,}\n{:,}\n{:,}"
        ees_value_field = {
            "name":   "Values",
            "value":  ees_value_field_description.format(ees.avg_attempts, ees.min_attempts, ees.max_attempts, ees.avg_meso_used, ees.min_meso_used, ees.max_meso_used),
            "inline": True,
        }

        ees_embed.add_field(**ees_label_field)
        ees_embed.add_field(**ees_value_field)
        ees_embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar.url)

        sfprot_label_field = {
            "name":   "Stats",
            "value":  "Average Used\nMinimum Used\nMaximum Used\nAverage VP/Credits Used\nMinimum VP/Credits Used\nMaximum VP/Credits Used",
            "inline": True,
	    }

        sfprot_value_field_description = "{:,.02f}\n{:,}\n{:,}\n{:,.02f}/{:,.02f}\n{:,}/{:,}\n{:,}/{:,}"
        sfprot_value_field = {
            "name":   "Values",
            "value":  sfprot_value_field_description.format(ees.avg_sfprots_used, ees.min_sfprots_used, ees.max_sfprots_used, ees.avg_vp_used, ees.avg_dp_used, ees.min_vp_used, ees.min_dp_used, ees.max_vp_used, ees.max_dp_used),
            "inline": True,
        }
        
        sfprot_embed = NormalEmbed(
            title="EES Simulator",
            description="Took {:,.02f} SF protects on average over {:,} samples to go from {}* to {}*".format(ees.avg_sfprots_used, static.LOSSDIA_EES_SAMPLES, start, end),
            author=ctx.author,
        )

        sfprot_embed.add_field(**sfprot_label_field)
        sfprot_embed.add_field(**sfprot_value_field)
        return await ctx.send(embeds=[ees_embed, sfprot_embed,])


async def setup(bot: LossdiaFAQ) -> None:
    await bot.add_cog(Utility(bot))
