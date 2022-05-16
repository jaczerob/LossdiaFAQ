from discord.ext import commands

from lossdiafaq.client import LossdiaFAQ

class AdminCog(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: LossdiaFAQ) -> None:
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        return await self.bot.is_owner(ctx.author)

    @commands.group(
        name="admin",
        description="the base admin extension command",
    )
    async def admin_group(self, _):
        return

    @admin_group.command(
        name="restart",
        description="restarts the bot",
    )
    async def _restart(self, ctx: commands.Context):
        await ctx.send("restarting")
        return await self.bot.close()

    @admin_group.command(
        name="sync",
        description="syncs all application commands",
    )
    async def _sync(self, ctx: commands.Context):
        await self.bot.tree.sync()
        await ctx.send("synced!")

    @admin_group.command(
        name="say",
        description="makes the bot say some text",
    )
    async def _say(self, ctx: commands.Context, *, text: str):
        return await ctx.send(text)

    @admin_group.group(
        name="extension",
        description="shows all loaded extensions",
    )
    async def extensions_group(self, ctx: commands.Context):
        if ctx.invoked_subcommand:
            return
            
        extensions = ", ".join(self.bot.extensions.keys())
        text = f"The following extensions are loaded: {extensions}"
        return await ctx.send(text)

    @extensions_group.command(
        name="unload",
        usage="<extension>",
        description="unloads an extension",
    )
    async def _unload(self, ctx: commands.Context, extension: str):
        if not extension.startswith("lossdiafaq.extensions."):
            extension = "lossdiafaq.extensions." + extension
        
        await self.bot.unload_extension(extension)
        return await ctx.send("extension unloaded")

    @extensions_group.command(
        name="reload",
        usage="<extension>",
        description="reloads an extension",
    )
    async def _reload(self, ctx: commands.Context, extension: str):
        if not extension.startswith("lossdiafaq.extensions."):
            extension = "lossdiafaq.extensions." + extension
        
        await self.bot.reload_extension(extension)
        return await ctx.send("extension reloaded")

    @extensions_group.command(
        name="load",
        usage="<extension>",
        description="loads an extension",
    )
    async def _load(self, ctx: commands.Context, extension: str):
        if not extension.startswith("lossdiafaq.extensions."):
            extension = "lossdiafaq.extensions." + extension
        
        await self.bot.load_extension(extension)
        return await ctx.send("extension loaded")



async def setup(bot: LossdiaFAQ) -> None:
    await bot.add_cog(AdminCog(bot))
