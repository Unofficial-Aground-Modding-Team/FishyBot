import asyncio
import os
from pathlib import Path

from discord.utils import setup_logging
import discord.ext.commands as commands

from fishybot.bot import FishyBot
from fishybot.database import create_session

DB_FILE = Path.cwd() / "fancyfish.sqlite"

async def main():
    async with create_session(str(DB_FILE.resolve())) as session_pool:
        bot = FishyBot(session_pool)
        setup_logging()
        await bot.load_extensions()

        @bot.command()
        @commands.is_owner()
        async def sync(ctx: commands.Context) -> None:
            """Sync commands"""
            guild_id = ctx.guild
            assert guild_id is not None
            bot.tree.copy_global_to(guild=guild_id)
            synced = await bot.tree.sync(guild=guild_id)
            await ctx.send(f"Synced {len(synced)} commands for this server")

        @bot.command()
        @commands.is_owner()
        async def reload(ctx: commands.Context) -> None:
            """Reload Extensions"""
            await bot.reload_extensions()
            await ctx.send("Reloaded extensions", ephemeral=True)

        await bot.start(os.environ['BOT_TOKEN'])

asyncio.run(main())