import asyncio
import math
import re
from datetime import datetime, timedelta

import hikari
import lightbulb
from lightbulb import commands

from extensions.utils import simulate_ees
from extensions.utils import calc_magic


plugin = lightbulb.Plugin('Utilities', 'Utility commands and handlers')


@plugin.command()
@lightbulb.option('args', 'Optional arguments for spell modifiers', default=None)
@lightbulb.option('spell_attack', 'Your spell\'s magic damage', type=int)
@lightbulb.option('hp', 'The monster\'s HP', type=int)
@lightbulb.command('magic', 'Shows how much magic is needed to one shot a monster with given HP')
@lightbulb.implements(commands.PrefixCommand)
async def magic(ctx: lightbulb.context.Context):
    hp, spell_attack, args = ctx.options.hp, ctx.options.spell_attack, ctx.options.args
    modifiers_msg = f'Spell Attack: {spell_attack}\n'
    modifier = 1.0 * spell_attack

    if args:
        if re.search(r'-[^ls]*[ls][^ls]*', args):  # loveless or elemental staff
            modifier *= 1.25
            modifiers_msg += f'Staff Multiplier: 1.25x\n'
        if re.search(r'-[^e]*e[^e]*', args):  # elemental advantage
            modifier *= 1.50
            modifiers_msg += f'Elemental Advantage: 1.50x\n'
        elif re.search(r'-[^d]*d[^d]*', args):  # elemental disadvantage
            modifier *= 0.50
            modifiers_msg += f'Elemental Disadvantage: 0.50x\n'

    magic_msg = ''

    if args and re.search(r'-[^a]*a[^a]*', args):  # elemental amp
        modifiers_msg += f'BW Elemental Amp: 1.30x\n'
        modifiers_msg += f'FP/IL Elemental Amp: 1.40x\n\n'

        # F/P and I/L
        fpil_magic = calc_magic(monster_hp=hp, modifier=modifier * 1.4)
        magic_msg += f'Magic for F/P or I/L: {fpil_magic}\n'

        # BW
        bw_magic = calc_magic(monster_hp=hp, modifier=modifier * 1.3)
        magic_msg += f'Magic for BW: {bw_magic}'
    else:
        magic = calc_magic(monster_hp=hp, modifier=modifier)
        magic_msg += f'\nMagic: {magic}'

    embed = hikari.Embed(title='Magic Calculator',
                        description=f'The magic required to one shot a monster with {hp} HP')
    embed.add_field(name='Magic Required', value=magic_msg, inline=True)
    embed.add_field(name='Modifiers', value=modifiers_msg, inline=True)
    embed.set_author(name=f'{ctx.author}', icon=ctx.author.avatar_url)

    await ctx.respond(embed=embed)


@magic.set_error_handler()
async def on_error(event: lightbulb.CommandErrorEvent):
    error = event.exception
    if error in (lightbulb.errors.NotEnoughArguments, lightbulb.errors.ConverterFailure):
        return await event.context.respond(
            f'Usage: $magic <hp> <spell attack> <args>\n'
            f'Args:\n'
            f'\t-a: Elemental Amplification\n'
            f'\t-l: Loveless Staff\n'
            f'\t-s: Elemental Staff\n'
            f'\t-e: Elemental Advantage\n'
            f'\t-d: Elemental Disadvantage\n\n'
            f'Example Usage: $magic 43376970 570 -al'
        )


@plugin.command()
@lightbulb.command('time', 'Displays the current server time')
@lightbulb.implements(lightbulb.PrefixCommand)
async def time(ctx: lightbulb.context.Context):
    time = datetime.utcnow().strftime('%d %b, %Y %H:%M:%S')

    tomorrow = datetime.utcnow() + timedelta(1)
    midnight = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day,
                        hour=0, minute=0, second=0)
    reset_delta = (midnight - datetime.utcnow())
    time_until_reset = str(reset_delta).split('.')[0]

    return await ctx.respond(f'The current server time is: {time}\nTime until reset: {time_until_reset}')


@plugin.command()
@lightbulb.option('member', 'Optional member to grab ID from', type=lightbulb.MemberConverter, default=None)
@lightbulb.command('id', 'Displays your Discord ID')
@lightbulb.implements(lightbulb.PrefixCommand)
async def id_(ctx: lightbulb.context.Context):
    member = ctx.options.member or ctx.author
    return await ctx.respond(f'{member}\'s Discord ID is **{member.id}**. Type `@discord` in game '
                            f'and enter this ID into the prompt to link your in-game account to your Discord account.')


@plugin.command()
@lightbulb.command('online', 'Displays the game\'s current online count')
@lightbulb.implements(lightbulb.PrefixCommand)
async def online(ctx: lightbulb.context.Context):
    guild = ctx.get_guild()
    if not guild or guild.id != plugin.bot.d.config['bot']['guild']:
        return await ctx.respond('This command may only be used in the Lossdia Discord Server.')

    lossdia_bot = guild.get_member(plugin.bot.d.config['bot']['lossdia-bot'])
    if not lossdia_bot or not lossdia_bot.get_presence():
        return await ctx.respond('I cannot get the online count currently.')

    online_count = lossdia_bot.get_presence().activities[0].name.split(' ')[3]
    return await ctx.respond(f'Online Users: {online_count}')


@plugin.command()
@lightbulb.option('samples', 'How many trials to do (default = 10,000)', type=int, default=10_000)
@lightbulb.option('protect_delta', 'The amount of stars before the checkpoints to start using star protection scrolls', type=int)
@lightbulb.option('ees', 'The start-end stars')
@lightbulb.command('ees', 'Simulates EES from start to end')
@lightbulb.implements(lightbulb.PrefixCommand)
async def ees_(ctx: lightbulb.context.Context):
    ees, protect_delta, samples = ctx.options.ees, ctx.options.protect_delta, ctx.options.samples
    start, end = map(int, ees.split('-'))

    if samples > 10_000:
        return await ctx.respond(f'{ctx.author.mention}, please keep samples to a maximum of 10,000.')
    elif start < 0 or end > 15:
        return await ctx.send(f'{ctx.author.mention}, stars must be a minimum of 0 and a maximum of 15.')

    message = await ctx.respond(f'Running simulation of EES from {start}* to {end}* {samples} times...')
    result = await asyncio.get_running_loop().run_in_executor(None, simulate_ees, ees, protect_delta, samples)
    await message.delete()

    ees_meso_cost = 175_000_000
    sfprot_dp_cost = 2_500
    sfprot_vp_cost = 5

    def roundup(x):
        return int(math.ceil(x / 10_000.0)) * 10_000

    embed = hikari.Embed(title='EES Simulator', description=result['description'])
    embed.add_field(
        name='EES',
        value=f'Average Used: {result["ees_average"]:,.2f}\nMinimum Used: {result["ees_min"]:,}\nMaximum Used: {result["ees_max"]:,}\n\nAverage Meso Used: {ees_meso_cost * result["ees_average"]:,.2f}\nMinimum Meso Used: {ees_meso_cost * result["ees_min"]:,}\nMaximum Meso Used: {ees_meso_cost * result["ees_max"]:,}'
    )

    embed.add_field(
        name='Starforce Protection Scrolls',
        value=f'Average Used: {result["sfprot_average"]:,.2f}\nMinimum Used: {result["sfprot_min"]:,}\nMaximum Used: {result["sfprot_max"]:,}\n\nAverage VP/Credits Used: {sfprot_vp_cost * result["sfprot_average"]:,.2f}/{roundup(sfprot_dp_cost * result["sfprot_average"]):,}\nMinimum VP/Credits Used: {sfprot_vp_cost * result["sfprot_min"]:,}/{roundup(sfprot_dp_cost * result["sfprot_min"]):,}\nMaximum VP/Credits Used: {sfprot_vp_cost * result["sfprot_max"]:,}/{roundup(sfprot_dp_cost * result["sfprot_max"]):,}'
    )

    embed.set_author(name=f'{ctx.author}', icon=ctx.author.avatar_url)
    return await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
