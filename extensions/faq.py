import asyncio
from email import message
from typing import Optional

import hikari
import lightbulb
from lightbulb import commands


@lightbulb.Check
def faq_check(ctx: lightbulb.Context):
    if ctx.user.id == 476226626464645135:
        return True

    if ctx.member is None:
        return False

    return ctx.member.get_top_role().permissions.any(hikari.Permissions.MANAGE_MESSAGES)


plugin = lightbulb.Plugin('FAQ', 'FAQ commands and handlers')
plugin.add_checks(faq_check)


def check(bot_channel: hikari.GuildTextChannel, message_channel: hikari.GuildTextChannel, member: hikari.Member):
    if member.id == 476226626464645135:
        return True

    if not isinstance(message_channel, hikari.GuildTextChannel):
        return True

    if message_channel.id == bot_channel.id:
        return True

    return member.get_top_role().permissions.any(hikari.Permissions.MANAGE_MESSAGES)


@plugin.listener(hikari.MessageCreateEvent)
async def faq_handler(message: hikari.MessageCreateEvent):
    prefix = plugin.bot.d.config['bot']['prefix']
    content = message.content
    command = content[len(prefix):].split(' ')[0]
    if not content.startswith(prefix) or plugin.bot.get_prefix_command(command):
        return

    if message.is_bot or not plugin.bot.d.db.is_connected() or not message.channel_id:
        return

    bot_channel_id = plugin.bot.d.config['bot'][ 'channel']
    guild_id = plugin.bot.d.config['bot']['guild']
    bot_channel: hikari.GuildTextChannel = await plugin.bot.rest.fetch_channel(bot_channel_id)
    message_channel: hikari.GuildTextChannel = await plugin.bot.rest.fetch_channel(message.channel_id)
    guild: hikari.Guild = await message_channel.fetch_guild()

    if guild.id == guild_id:
        member = guild.get_member(message.author_id)
        if not check(bot_channel, message_channel, member):
            event = await message_channel.send(f'Please use the bot channel, {member.mention}.')
            await asyncio.sleep(5)
            return await event.delete()


    await send_faq(message_channel, command)


@plugin.command()
@lightbulb.option('command', 'The command to invoke', default=None)
@lightbulb.command('faq', 'Invokes a FAQ command')
@lightbulb.implements(lightbulb.PrefixCommand)
async def faq(ctx: lightbulb.Context) -> None:
    if channel := ctx.get_channel():
        command = ctx.options.command
        await send_faq(channel, command)


async def send_faq(message_channel: hikari.GuildTextChannel, command: Optional[str]):
    if command is None:
        all_commands = await plugin.bot.d.db.request_all()
        fmt = ' | '.join(all_commands)[:-3]
        return await message_channel.send(f'Here are all our FAQ commands\n```\n{fmt}\n```')

    if not (resp := await plugin.bot.d.db.request(command)):
        return

    if not isinstance(resp, str):
        return

    embed = hikari.Embed(title=command, description=resp, color=hikari.Color.from_hex_code('#bbbefe'))
    embed.set_footer('Ask (DO NOT PING) olivia rodrigo or a staff member to $add or $update a command if you want!')
    return await message_channel.send(embed=embed)


@plugin.command()
@lightbulb.option('description', 'The description of the command', modifier=commands.OptionModifier.CONSUME_REST)
@lightbulb.option('command', 'The command to add')
@lightbulb.command('add', 'Adds a FAQ command')
@lightbulb.implements(lightbulb.PrefixCommand)
async def add(ctx: lightbulb.Context) -> None:
    command, description = ctx.options.command, ctx.options.description
    await plugin.bot.d.db.create(command, description)
    return await ctx.respond(f'{command} added.')


@plugin.command()
@lightbulb.option('description', 'The description of the command', modifier=commands.OptionModifier.CONSUME_REST)
@lightbulb.option('command', 'The command to update')
@lightbulb.command('update', 'Updates a FAQ command')
@lightbulb.implements(lightbulb.PrefixCommand)
async def update(ctx: lightbulb.Context) -> None:
    command, description = ctx.options.command, ctx.options.description
    await plugin.bot.d.db.update(command, description)
    return await ctx.respond(f'{command} updated.')


@plugin.command()
@lightbulb.option('command', 'The command to add')
@lightbulb.command('delete', 'Deletes a FAQ command')
@lightbulb.implements(lightbulb.PrefixCommand)
async def add(ctx: lightbulb.Context) -> None:

    command = ctx.options.command
    await plugin.bot.d.db.delete(command)
    return await ctx.respond(f'{command} deleted.')


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
    