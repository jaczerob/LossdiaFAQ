import lightbulb
from lightbulb import commands


plugin = lightbulb.Plugin('Admin', 'Internal bot commands')
plugin.add_checks(lightbulb.checks.owner_only)


@plugin.command()
@lightbulb.command('admin', 'The base admin command')
@lightbulb.implements(commands.PrefixCommandGroup)
async def admin(ctx: lightbulb.context.Context) -> None:
    return await ctx.respond('Type "$help admin" for admin commands')


@admin.child()
@lightbulb.command('shutdown', 'Shuts down the bot')
@lightbulb.implements(commands.PrefixSubCommand)
async def shutdown(ctx: lightbulb.context.Context) -> None:
    return await plugin.bot.close()


@admin.child()
@lightbulb.option('phrase', 'The phrase to make the bot repeat', modifier=commands.OptionModifier.CONSUME_REST)
@lightbulb.command('say', 'Make the bot say something in the current channel')
@lightbulb.implements(commands.PrefixSubCommand)
async def say(ctx: lightbulb.context.Context) -> None:
    return await ctx.respond(ctx.options.phrase)


@admin.child()
@lightbulb.command('extensions', 'A group of extensions-based commands')
@lightbulb.implements(commands.PrefixSubGroup)
async def extensions(ctx: lightbulb.context.Context) -> None:
    return await ctx.respond(f'The following extensions are loaded: {", ".join(plugin.bot.extensions)}.')


@extensions.child()
@lightbulb.option('extension', 'The extension to unload', str)
@lightbulb.command('unload', 'Unloads an extension')
@lightbulb.implements(commands.PrefixSubCommand)
async def unload_ext(ctx: lightbulb.context.Context) -> None:
    extension = ctx.options.extension
    plugin.bot.unload_extensions(extension)
    return await ctx.respond(f'{extension} unloaded.')


@extensions.child()
@lightbulb.option('extension', 'The extension to reload', str)
@lightbulb.command('reload', 'Reloads an extension')
@lightbulb.implements(commands.PrefixSubCommand)
async def reload(ctx: lightbulb.context.Context) -> None:
    extension = ctx.options.extension
    plugin.bot.reload_extensions(extension)
    await ctx.respond(f'{extension} reloaded.')


@extensions.child()
@lightbulb.option('extension', 'The extension to load', str)
@lightbulb.command('load', 'Loads an extension')
@lightbulb.implements(commands.PrefixSubCommand)
async def load_ext(ctx: lightbulb.context.Context) -> None:
    extension = ctx.options.extension
    plugin.bot.load_extensions(extension)
    return await ctx.respond(f'{extension} loaded.')


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)