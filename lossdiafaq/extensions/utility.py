from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Optional

from discord.ext import commands
import discord.utils

from lossdiafaq import static
from lossdiafaq.client import LossdiaFAQ
from lossdiafaq.services.calculator.ees import EESArgumentError, EESCalculator
from lossdiafaq.services.calculator.flame import FlameCalculator
from lossdiafaq.services.calculator.magic import FlagError, MagicCalculator
from lossdiafaq.services.discord.embed import NormalEmbed, EmbedField, ErrorEmbed
from lossdiafaq.services.discord.context import Context


class Utility(commands.Cog):
    def __init__(self, bot: LossdiaFAQ) -> None:
        self.bot = bot
        self.ees_executor = ThreadPoolExecutor(max_workers=3)

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.in_dm:
            return True

        if not ctx.in_lossdia or ctx.in_bot_channel:
            return True

        return ctx.is_owner or ctx.is_moderator

    @commands.hybrid_command(
        name="magic",
        description="shows how much magic is needed to one shot a monster with given HP",
        usage="<hp> <spell attack> [<flags>]",
    )
    async def _magic(self, ctx: Context, hp: int, spell_attack: int, *, flags: Optional[str]):
        """shows how much magic is needed to one shot a monster with given HP

        flags include (not in any order):
        -l: loveless staff
        -s: elemental staff
        -e: elemental advantage  
        -d: elemental disadvantage
        -a: elemental amp (if absent, will only show magic for Bishop, otherwise will only show magic for BW, FP, and IL)

        examples:
        $magic x x -al means you are testing with elemental amp and loveless staff ONLY for BW, FP, and IL
        
        $magic x x -l means you are testing with a loveless staff ONLY for BS
        """

        if ctx.interaction is not None:
            await ctx.defer()

        magic = MagicCalculator(hp, spell_attack, flags)
        try:
            magic.calculate()
        except FlagError as error:
            return await ctx.reply(embed=ErrorEmbed(
                title="Flag Error",
                description=str(error),
            ))

        if magic.flags.empty:
            magic_embed_description = f"The magic required to one shot a monster with {hp:,} HP and {spell_attack:,} spell attack"
        else:
            modifier_message = ''

            if magic.flags.has_amp:
                modifier_message += "Elemental Amplification (BW {:.02f} / FP/IL {:.02f})\n".format(static.LOSSDIA_MAGIC_BW_ELEMENTAL_AMP_MULTIPLIER, static.LOSSDIA_MAGIC_FPIL_ELEMENTAL_AMP_MULTIPLIER)
            
            if magic.flags.has_adv:
                modifier_message += "Elemental Advantage ({:.02f})\n".format(static.LOSSDIA_MAGIC_ELEMENTAL_ADVANTAGE_MULTIPLIER)
            
            if magic.flags.has_disadv:
                modifier_message += "Elemental Disadvantage ({:.02f})\n".format(static.LOSSDIA_MAGIC_ELEMENTAL_DISADVANTAGE_MULTIPLIER)
            
            if magic.flags.has_staff:
                modifier_message += "Staff Multiplier ({:.02f})\n".format(static.LOSSDIA_MAGIC_STAFF_MULTIPLIER)

            magic_embed_description = f"The magic required to one shot a monster with {hp:,} HP and {spell_attack:,} spell attack with modifiers:\n\n{modifier_message.strip()}"

        magic_embed = NormalEmbed(
            title="Magic Calculator",
            description=magic_embed_description,
            author=ctx.author,
        )
        
        class_field = EmbedField(
            name="Class",
            value='',
            inline=True,
        )

        magic_field = EmbedField(
            name="Magic",
            value='',
            inline=True,
        )

        if magic.flags.has_amp:
            class_field.value = "BW\nI/L\nF/P"
            magic_field.value = "{:,}\n{:,}\n{:,}\n".format(magic.bw_magic, magic.fpil_magic, magic.fpil_magic)

        if not magic.flags.has_amp:
            class_field.value = "BS"
            magic_field.value = "{:,}".format(magic.bs_magic)

        magic_embed.add_field(class_field)
        magic_embed.add_field(magic_field)
        return await ctx.reply(embed=magic_embed)

    @commands.hybrid_command(
        name="time",
        description="displays the current server time",
    )
    async def _time(self, ctx: Context):
        """displays the current server time"""
        time = datetime.utcnow().strftime('%d %b, %Y %H:%M:%S')

        tomorrow = datetime.utcnow() + timedelta(1)
        midnight = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day,
                            hour=0, minute=0, second=0)
        reset_delta = (midnight - datetime.utcnow())
        time_until_reset = str(reset_delta).split('.')[0]
        
        embed = NormalEmbed(title="Server Time", description=f"The current server time is: {time} UTC\nTime until reset: {time_until_reset}", author=ctx.author)
        return await ctx.reply(embed=embed)

    @commands.hybrid_command(
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

    @commands.hybrid_command(
        name="flame",
        description="shows the flame range for a certain level of gear",
        usage="<item level>",
        aliases=["flames",]
    )
    async def _flame(self, ctx: Context, level: int):
        """shows the flame range for a certain level of gear"""

        flames = FlameCalculator(level)
        flames.calculate()

        flames_embed = NormalEmbed(
            title="Flames Calculator",
            description=f"The flame stats for a level {level} item. Overall stats are double that of normal items.",
            author=ctx.author,
        )

        eflame_field = EmbedField(
            name="Eternal Flame Stat Range",
            value="Overall: {} - {}\nNot Overall: {} - {}".format(flames.overall_eflame_min_stats, flames.overall_eflame_max_stats, flames.item_eflame_min_stats, flames.item_eflame_max_stats),
            inline=False,
        )

        pflame_field = EmbedField(
            name="Powerful Flame Stat Range",
            value="Overall: {} - {}\nNot Overall: {} - {}".format(flames.overall_pflame_min_stats, flames.overall_pflame_max_stats, flames.item_pflame_min_stats, flames.item_pflame_max_stats),
            inline=False,
        )

        flames_embed.add_field(eflame_field)
        flames_embed.add_field(pflame_field)
        return await ctx.reply(embed=flames_embed)

    @commands.hybrid_command(
        name="ees",
        description="simulates EES from start to end",
        usage="<start> <end> <protect delta>",
    )
    async def _ees(self, ctx: Context, start: int, end: int, protect_delta: int):
        """simulates EES from start to end
        
        start must be a number between 0 and 14
        end must be a number between 1 and 15
        protect delta must be a number between 0 and 4

        protect delta is the number of stars before a safety point (10, 15) where you will use a SF Prot scroll
        """

        if ctx.interaction is not None:
            await ctx.defer()

        ees = EESCalculator(start, end, protect_delta)
        message = await ctx.reply(f'Running simulation of EES from {start}* to {end}* {static.LOSSDIA_EES_SAMPLES} times...')
        
        try:
            await self.bot.loop.run_in_executor(self.ees_executor, ees.simulate)
            await message.delete()
        except EESArgumentError as error:
            await message.delete()
            return await ctx.reply(embed=ErrorEmbed(
                title="EES Simulator Argument Error",
                description=str(error),
            ))

        ees_embed = NormalEmbed(
            title="EES Simulator",
            description="Took {:,.02f} EES on average over {:,} samples to go from {}* to {}*".format(ees.avg_attempts, static.LOSSDIA_EES_SAMPLES, start, end),
            author=ctx.author,
        )

        ees_label_field = EmbedField(
            name=  "Stats",
            value= "Average Used\nMinimum Used\nMaximum Used\nAverage Meso Used\nMinimum Meso Used\nMaximum Meso Used",
            inline=True,
        )

        ees_value_field_description = "{:,.02f}\n{:,}\n{:,}\n{:,}\n{:,}\n{:,}"
        ees_value_field = EmbedField(
            name="Values",
            value=ees_value_field_description.format(ees.avg_attempts, ees.min_attempts, ees.max_attempts, ees.avg_meso_used, ees.min_meso_used, ees.max_meso_used),
            inline=True,
        )

        ees_embed.add_field(ees_label_field)
        ees_embed.add_field(ees_value_field)
        embeds = [ees_embed, ]

        if ees.avg_sfprots_used > 0.0:
            sfprot_label_field = EmbedField(
                name=  "Stats",
                value= "Average Used\nMinimum Used\nMaximum Used\nAverage VP/Credits Used\nMinimum VP/Credits Used\nMaximum VP/Credits Used",
                inline=True,
            )

            sfprot_value_field_description = "{:,.02f}\n{:,}\n{:,}\n{:,.02f}/{:,.02f}\n{:,}/{:,}\n{:,}/{:,}"
            sfprot_value_field = EmbedField(
                name=  "Values",
                value= sfprot_value_field_description.format(ees.avg_sfprots_used, ees.min_sfprots_used, ees.max_sfprots_used, ees.avg_vp_used, ees.avg_credits_used, ees.min_vp_used, ees.min_credits_used, ees.max_vp_used, ees.max_credits_used),
                inline=True,
            )
            
            sfprot_embed = NormalEmbed(
                title="EES Simulator",
                description="Took {:,.02f} SF protects on average over {:,} samples to go from {}* to {}*".format(ees.avg_sfprots_used, static.LOSSDIA_EES_SAMPLES, start, end),
            )

            sfprot_embed.add_field(sfprot_label_field)
            sfprot_embed.add_field(sfprot_value_field)
            embeds.append(sfprot_embed)

        return await ctx.reply(embeds=embeds)

    @commands.hybrid_command(
        name="user",
        description="shows your user info",
    )
    async def _user(self, ctx: Context):
        """shows your user info"""
        if ctx.guild is None:
            return await ctx.reply("Must be used in the Windia Discord server.", delete_after=5.0)

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
        guild_information_field.value += f"Join position: {join_position}/{ctx.guild.member_count}\n"

        if ctx.author.premium_since:
            boosted_since = discord.utils.format_dt(ctx.author.premium_since)
            boosted_since_relative = discord.utils.format_dt(ctx.author.premium_since, style="R")
            guild_information_field.value += f"Boosted {ctx.guild} since {boosted_since} ({boosted_since_relative})"

        embed.add_field(guild_information_field)
        return await ctx.reply(embed=embed)


async def setup(bot: LossdiaFAQ) -> None:
    await bot.add_cog(Utility(bot))
