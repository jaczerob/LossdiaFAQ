import asyncio
import functools

from async_timeout import timeout
from discord.ext import commands
from loguru import logger

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

        try:
            async with timeout(5.0):
                logger.info("sending command: {} (args={}, kwargs={})", command, args, kwargs)
                await ctx.bot.tcp.send_command(command, *args, **kwargs)
        except asyncio.TimeoutError as exc:
            logger.opt(exception=exc).error("failed to send command")
            return

        try:
            async with timeout(5.0):
                logger.info("waiting for response from server for command: {}", command)
                resp = await ctx.bot.tcp.wait_response()
        except asyncio.TimeoutError as exc:
            logger.opt(exception=exc).error("server timeout")
            return

        logger.info("got response from server for command: {}", command)
        return await ctx.reply(resp.content, embeds=resp.embeds())
