from deta_discord_interactions import DiscordInteractionsBlueprint
from deta_discord_interactions import Message, Embed
from deta_discord_interactions import ActionRow, SelectMenu, SelectMenuOption
from deta_discord_interactions import Autocomplete, Option, Choice
from deta_discord_interactions import Context
from deta_discord_interactions.enums import PERMISSION



from common.config import BOT_COLOR
from common.exceptions import GameNotFoundError
from database.sqlite_model import GameRecord
from database.operations import get_possible_games, get_possible_tags, get_exact_record, get_matching_records

bp = DiscordInteractionsBlueprint()


def list_search_menu(data: list[GameRecord]):
    options = []

    for item in data:
        options.append(SelectMenuOption(
            label=item.id,
            value=f"{item.id}@{item.tag}@{item.game_id}",
            description=item.path,
        ))

    return SelectMenu(
        "select_data_ih",
        options,
        placeholder="Select one...",
    )


@bp.custom_handler("select_data_ih")
def dropdown_callback(ctx: Context):
    id_, tag_, game_ = ctx.values[0].split("@")
    record = get_exact_record(game_, tag_, id_, include_xml=True, include_hidden=True)
    message = "```xml\n" + record.xml.strip() + "\n"
    if len(message) >= 1990:
        NL = "\n"
        message = message[:1600] + f"```...well, it was too long to display. See the full thing in: ```{NL}{record.path}{NL}```"
    else:
        message += "```"
    return Message(message, ephemeral=True)



@bp.command(
    name="fullsearch",
    description="Searches my database, including Hidden records",
    annotations = dict(
        game = "Which Game to look for.",
        tag = "Which XML <tag> to look for.",
        id = "The ID of the object.",
        public = "Send as a normal, not ephemeral message.",
    ),
    default_member_permissions=PERMISSION.MANAGE_MESSAGES,
)
def search_ih(
    ctx,
    game: Autocomplete[str],
    tag: Autocomplete[str],
    id: Autocomplete[str] = None,
    public: bool = False,
):
    """Searches my database for IDs and returns a dropdown menu with the matches."""
    records = get_matching_records(game, tag, id or '', include_xml=True, include_hidden=True)

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


@search_ih.autocomplete()
def autocomplete_search_ih(
    ctx,
    game: Option = None,
    tag: Option = None,
    id: Option = None,
):
    "Provides Autocompletion to /fullsearch"
    if game is not None and game.focused:
        games = get_possible_games(game.value, include_hidden=True)
        return [
            Choice(game.full_name, game.id)
            for game in games[:25]
        ]
    elif tag is not None and tag.focused:  # Game should ALWAYS be filled before tag
        try:
            return get_possible_tags(game.value, tag.value, include_hidden=True)[:25]
        except GameNotFoundError:
            return []
    elif id is not None and id.focused:  # Game and Tag should ALWAYS be filled before id
        records = get_matching_records(game.value, tag.value, id.value, include_xml=False, include_hidden=True, limit=25)
        return [record.id for record in records]
    else:
        return []
