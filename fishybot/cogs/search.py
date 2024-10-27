import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select

from fishybot.bot import FishyBot
from fishybot.database import GameRecord


class Search(commands.Cog):
    group = app_commands.Group(name="search", description="Search data from FancyFish games")

    def __init__(self, bot: FishyBot) -> None:
        self.bot = bot

    @group.command(name="id", description="Retrieve a element by ID")
    async def search_by_id(self, inter: discord.Interaction, game: str, tag: str, id: str) -> None:
        async with self.bot.database_connection() as session:
            results = await session.scalars(
                select(GameRecord)
                .where(GameRecord.game_id == game)
                .where(GameRecord.tag == tag)
                .where(GameRecord.id == id)
            )
            data = results.first()
        if data is None:
            await inter.response.send_message("Not found", ephemeral=True)
            return
        assert data is not None
        message = f"Found record in ``{data.path}``: ```xml\n{data.xml}\n```"
        await inter.response.send_message(message)

    @app_commands.command(name="echo", description="Echo a message")
    async def echo(self, inter: discord.Interaction, message: str) -> None:
        await inter.response.send_message(message, ephemeral=True)


async def setup(bot: FishyBot) -> None:
    await bot.add_cog(Search(bot))
