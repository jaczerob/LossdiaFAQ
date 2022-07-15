import functools

from discord.ext import commands
from loguru import logger
from client.windiafaq.discord.embed import ErrorEmbed
from client.windiafaq.tcp.response import ServerResponseError

from windiafaq.discord import context


class TCPCommand(commands.Command):
    async def invoke(self, ctx: context.Context, /) -> None:
        new_callback = functools.partial(self.invoke_tcp_command, *ctx.args, *ctx.kwargs)
        functools.update_wrapper(new_callback, ctx.command.callback)
        ctx.command.callback = new_callback
        return await super().invoke(ctx)

    async def invoke_tcp_command(self, _: commands.Cog, ctx: context.Context, *args, **kwargs):
        if ctx.invoked_parents:
            command = ctx.invoked_parents[0]
            args = [ctx.command.name] + args
        else:
            command = ctx.command.name

        logger.info("sending command: {} (args={}, kwargs={})", command, args, kwargs)
        await ctx.bot.tcp.send_command(command, *args, **kwargs)

        try :
            logger.info("waiting for response from server for command: {}", command)
            resp = await ctx.bot.tcp.wait_response()
        except ServerResponseError as e:
            return await ctx.reply(embed=ErrorEmbed(title="Command Error!", description=str(e)))
        else:
            return await ctx.reply(resp.content, embeds=resp.embeds())
        finally:
            logger.info("got response from server for command: {}", command)
