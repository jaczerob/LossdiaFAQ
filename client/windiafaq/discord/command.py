import functools

from discord.ext import commands

from windiafaq.discord import context


class IPCCommand(commands.Command):
    async def invoke(self, ctx: context.Context, /) -> None:
        new_callback = functools.partial(self.invoke_ipc_command, *ctx.args, *ctx.kwargs)
        functools.update_wrapper(new_callback, ctx.command.callback)
        ctx.command.callback = new_callback
        return await super().invoke(ctx)

    async def invoke_ipc_command(self, _: commands.Cog, ctx: context.Context, *args, **kwargs):
        if ctx.invoked_parents:
            command = ctx.invoked_parents[0]
            args = [ctx.command.name] + args
        else:
            command = ctx.command.name

        await ctx.bot.ipc.send_command(command, *args, **kwargs)
        resp = await ctx.bot.ipc.wait_response()
        return await ctx.reply(resp.content, embeds=resp.embeds())
