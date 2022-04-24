import asyncio
import traceback

import hikari
import lightbulb
import lightbulb.utils
import yaml

from database import FAQDatabase


with open('lossdia.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


token = config['bot']['secrets']['token']
prefix = config['bot']['prefix']

bot = lightbulb.BotApp(
    token=token, 
    prefix=prefix, 
    intents=hikari.Intents.ALL
)


def format_traceback(tb: str):
    tb = tb.replace('*', '\*').replace('_', '\_').replace('~', '\~')
    if len(tb) > 2000:
        old_tb = tb
        tb = tb[:1996] + '...'
        return old_tb, tb
    return None, tb



@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    exception = event.exception.__cause__ or event.exception
    if isinstance(exception, (lightbulb.errors.CommandNotFound, lightbulb.errors.NotEnoughArguments, lightbulb.errors.MissingRequiredPermission)):
       return 

    tb = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    old_tb, tb = format_traceback(tb)

    if logging_channel := await bot.rest.fetch_channel(config['bot']['logging']):
        await bot.rest.create_message(logging_channel, tb)

    print(old_tb if old_tb else tb)


@bot.check()
async def bot_channel_only(ctx: lightbulb.Context):
    if ctx.author.id == 476226626464645135:
        return True

    message_channel: hikari.GuildTextChannel = await bot.rest.fetch_channel(ctx.channel_id)
    if not isinstance(message_channel, hikari.GuildTextChannel):
        return False

    guild: hikari.Guild = await message_channel.fetch_guild()
    if not guild.id == bot.d.config['bot']['guild']:
        return True

    if message_channel.id == bot.d.config['bot']['channel']:
        return True

    member = guild.get_member(ctx.author.id)
    return member.get_top_role().permissions.any(hikari.Permissions.MANAGE_MESSAGES)


async def cleanup():
    await bot.d.db.disconnect()


async def main():
    bot.d.config = config
    bot.d.db = FAQDatabase(config['faq']['database'])
    bot.load_extensions_from(config['bot']['extensions'])
    
    await bot.d.db.connect()

    try:
        await bot.start()
        await bot.join()
    finally:
        await cleanup()


if __name__ == '__main__':
    asyncio.run(main())
