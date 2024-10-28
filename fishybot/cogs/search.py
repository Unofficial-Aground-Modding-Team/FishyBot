from difflib import SequenceMatcher as SM
import typing

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select

from fishybot.bot import FishyBot
from fishybot.database import Game, GameRecord
from fishybot.utils.xpath import filter_records

def _build_scorer[T](reference: str, converter: typing.Callable[[T], str], *, fast: bool = False) -> typing.Callable[[T], float]:
    "Return a function for usage in sorted(key=...)"
    if fast:
        def scorer(value: T) -> float:
            string = converter(value)
            return string.startswith(reference) + SM(lambda x: x == ' ', reference, string).real_quick_ratio()
    else:
        def scorer(value: T) -> float:
            string = converter(value)
            return string.startswith(reference) + SM(lambda x: x == ' ', reference, string).ratio()
    return scorer

def _parse_options(interaction: discord.Interaction, option_name: str) -> str | None:
    "Retrieve an option argument from the Interaction"
    if interaction.data is None:
        return None
    options = interaction.data.get("options")
    if options is None:
        return None
    for option in (subopt for opt in options for subopt in opt.get("options", [])):
        if option.get("name") == option_name:
            result = option.get("value")
            assert isinstance(result, str)
            return result

def _format_record_display_name(record: GameRecord) -> str:
    """Create a string displaying the Record ID and Path.
    Ommits the Path starting from the left if the result is larger than the accepted size."""
    id_size = len(record.id)
    path_size = len(record.path)
    total_size = id_size + path_size + 3
    if total_size <= 100:
        return f"{record.id} @ {record.path}"
    else:
        path = record.path[(-(100 - id_size - 6)):]
        return f"{record.id} @ ...{path}"


class Search(commands.Cog):
    group = app_commands.Group(name="search", description="Search data from FancyFish games")

    def __init__(self, bot: FishyBot) -> None:
        self.bot = bot

    @group.command(name="id", description="Retrieve a element by ID")
    async def search_by_id(self, inter: discord.Interaction, game: str, tag: str, id: str) -> None:
        await inter.response.defer()
        results = await self.bot.query(
            select(GameRecord)
            .where(GameRecord.game_id == game)
            .where(GameRecord.tag == tag)
            .where(GameRecord.id == id)
        )
        data = results.first()
        if data is None:
            await inter.response.send_message("Not found", ephemeral=True)
            return
        message = f"Found record in ``{data.path}``: ```xml\n{data.xml}\n```"
        if len(message) > 2000:
            message = f"Found record in ``{data.path}``: ```xml\n{data.xml.split('\n')[0]}\n``` But it is too large to send the entire thing"
        await inter.edit_original_response(content=message)


    @group.command(name="xpath", description="Retrieve a element by XPath")
    async def search_by_xpath(self, inter: discord.Interaction, game: str, tag: str, xpath: str) -> None:
        await inter.response.defer()
        results = await self.bot.query(
            select(GameRecord)
            .where(GameRecord.game_id == game)
            .where(GameRecord.tag == tag)
        )
        try:
            data = filter_records(results.fetchall(), xpath)
        except Exception as err:
            print(err)
            await inter.edit_original_response(content="Invalid xpath")
            return
        # TODO ADD A SELECT MENU COMPONENT
        if len(data) == 0:
            await inter.edit_original_response(content="Found no matching records")
        elif len(data) == 1:
            record = data[0]
            message = f"Found record in ``{record.path}``: ```xml\n{record.xml}\n```"
            if len(message) > 2000:
                message = f"Found record in ``{record.path}``: ```xml\n{record.xml.split('\n')[0]}\n``` But it is too large to send the entire thing"
            await inter.edit_original_response(content=message)
        else:
            # A) ID, Path and XML of each
            _formatted = [f"<!-- {record.id} @ {record.path} -->\n{record.xml}" for record in data]
            message = f"Found {len(data)} records: ```xml\n{'\n'.join(_formatted)}\n```"
            # B) ID and Path of each
            if len(message) > 2000:
                _formatted = [f"{record.id} @ {record.path}" for record in data]
                message = f"Found {len(data)} records: ```\n{'\n'.join(_formatted)}\n```"
            # C) ID of each
            if len(message) > 2000:
                _formatted = [record.id for record in data]
                message = f"Found {len(data)} records: ```\n{'\n'.join(_formatted)}\n```"
            # D) Bruh
            if len(message) > 2000:
                message = f"Found {len(data)} records."

            await inter.edit_original_response(content=message)


    @search_by_id.autocomplete("game")
    @search_by_xpath.autocomplete("game")
    async def autocomplete_game(self, inter: discord.Interaction, current: str) -> list[app_commands.Choice]:
        results = (await self.bot.query(select(Game))).fetchall()
        if results is None:
            return []
        return [
            app_commands.Choice(name=game.full_name, value=game.id)
            for game in sorted(results, key=_build_scorer(current, lambda game: game.full_name), reverse=True)
        ]

    @search_by_id.autocomplete("tag")
    @search_by_xpath.autocomplete("tag")
    async def autocomplete_tag(self, inter: discord.Interaction, current: str) -> list[app_commands.Choice]:
        selected_game = _parse_options(inter, "game")
        if selected_game is None:
            return []
        result = (await self.bot.query(select(Game).where(Game.id == selected_game))).first()
        if result is None:
            return []
        # P1: Public ; P0: Private (only used within mods)
        tags = [tag.removesuffix(':P1') for tag in result.data_types.split(", ") if tag.endswith("P1")]
        return [
            app_commands.Choice(name=tag, value=tag)
            for tag in sorted(tags, key=_build_scorer(current, lambda tag: tag), reverse=True)
        ][:25]

    @search_by_id.autocomplete("id")
    async def autocomplete_id(self, inter: discord.Interaction, current: str) -> list[app_commands.Choice]:
        selected_game = _parse_options(inter, "game")
        selected_tag = _parse_options(inter, "tag")
        if selected_game is None or selected_tag is None:
            return []

        records = (await self.bot.query(
            select(GameRecord)
            .where(GameRecord.game_id == selected_game)
            .where(GameRecord.tag == selected_tag)
            # .where(GameRecord.is_public == True)
        )).fetchall()
        if records is None:
            return []
        return [
            app_commands.Choice(name=_format_record_display_name(record), value=record.id)
            for record in sorted(records, key=_build_scorer(current, lambda record: record.id, fast=True), reverse=True)
        ][:25]


async def setup(bot: FishyBot) -> None:
    await bot.add_cog(Search(bot))
