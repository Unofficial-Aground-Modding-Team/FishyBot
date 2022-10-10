from deta_discord_interactions import DiscordInteractionsBlueprint
from deta_discord_interactions import Message, Embed
from deta_discord_interactions import ActionRow, SelectMenu, SelectMenuOption
from deta_discord_interactions import Autocomplete, Option, Choice
from deta_discord_interactions import Context

from common.config import BOT_COLOR
from common.exceptions import GameNotFoundError
from database.sqlite_model import GameRecord
from database.xml_operations import get_matching_records
from common.exceptions import InvalidQueryError
from database.operations import get_possible_games, get_possible_tags

bp = DiscordInteractionsBlueprint()


def list_search_menu(data: list[GameRecord]):
    options = []

    for item in data:
        options.append(SelectMenuOption(
            label=item.id,
            value=f"{item.id}@{item.tag}@{item.mod}@{item.game_id}",
            description=item.path,
        ))

    return SelectMenu(
        "select_data",
        options,
        placeholder="Select one...",
    )
    # Callback on search.py


@bp.command(
    name="xmlsearch",
    description="Searches my database using XPath. See /help xmlsearch",
    annotations = dict(
        game = "Which Game to look for.",
        tag = "Which XML <tag> to look for.",
        xpath = "The XPath query to match.",
        public = "Send as a normal, not ephemeral message.",
    )
)
def xml_search(
    ctx: Context,
    game: Autocomplete[str],
    tag: Autocomplete[str],
    xpath: str,
    public: bool = False,
):
    """Searches my database for IDs and returns a dropdown menu with the matches."""
    try:
        records = get_matching_records(game, tag, xpath, include_hidden=False)
    except InvalidQueryError:
        return Message("Bad query. Ping etrotta#3846 for help or more information.", ephemeral=True)

    if not records:  # No matches
        message = Message(
            embed = Embed(
                title="No matching data found",
                color=BOT_COLOR,
            ),
            ephemeral=not public,
        )
    elif len(records) == 1:  # One match
        message = "```xml\n" + records[0].xml.strip() + "\n```"
        if len(message) >= 2000:
            message = message[:1800] + "```\n.....well, it was too big to display all in one place. See the rest in {}".format(records[0].path)
        message = Message(message, ephemeral=not public)
    else:  # Many matches
        embed = Embed(title = f"Select which {tag} you want to see:", color = BOT_COLOR)
        component = list_search_menu(records)
        message = Message(
            embed=embed,
            components=[ActionRow([component])],
            ephemeral=not public,
            allowed_mentions={"parse": []},
        )

    return message


@xml_search.autocomplete()
def autocomplete_search(
    ctx,
    game: Option = None,
    tag: Option = None,
    **_,
):
    "Provides Autocompletion to /xml_search"
    if game is not None and game.focused:
        games = get_possible_games(game.value, include_hidden=False)
        return [
            Choice(game.full_name, game.id)
            for game in games[:25]
        ]
    elif tag is not None and tag.focused:  # Game should ALWAYS be filled before tag
        try:
            return get_possible_tags(game.value, tag.value, include_hidden=False)[:25]
        except GameNotFoundError:
            return []
    else:
        return []
