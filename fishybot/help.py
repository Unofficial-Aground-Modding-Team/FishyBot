from deta_discord_interactions import DiscordInteractionsBlueprint
from deta_discord_interactions import Context, Option, Choice
from deta_discord_interactions import Message
from deta_discord_interactions import Embed, embed

from common.config import BOT_COLOR

search_help = """Searches for game records in the database.
For example, if you want to find the Aground record ```xml
<item id="gold_bar" type="resource" cost="250" weight="5" icon="gold_bar.ico" />
```
You there you have `game=aground`, `tag=item` and `item=gold_bar`, so you can find it by typing `/search aground item gold_bar`.
The bot may offer Autocompletion options with a small delay after you start typing a command.
If there are multiple matches to your search query, it will return a Select Menu with up to 25 items that matched it.
**Note:** Until I double check the boundaries with terra, this command will not return any records from the Full Version of the game or any other mods.
"""


xml_search_help = Embed(
    title="XML Search Help",
    description="Searches for game records in the database that matches [XPath filters supported by Python](https://docs.python.org/3/library/xml.etree.elementtree.html#supported-xpath-syntax).",
    color=BOT_COLOR,
    fields=[
        embed.Field(
            "Matching attributes examples",
            """Items with (any) attack: `/xmlsearch aground item [@attack]`\n"""
            """Items with 0 cost: `/xmlsearch aground item [@cost="0"]`\n"""
            """Enchantment recipes: `/xmlsearch aground recipe [@type="magic_forge"]`"""
        ),
        embed.Field(
            "Matching children examples",
            """Items that modify your stats: `/xmlsearch aground item .//stat`. Also works with just `stat`, `[stat]` or `//stat`\n"""
            """Items with temporary buffs: `/xmlsearch aground item stat[@time]`\n"""
            """Items with permanent buffs: `/xmlsearch aground item stat[@max]`\n"""
            """Items with an <action> with a <tile>: `/xmlsearch aground item ./action/tile`"""
        ),
    ]
)


help_messages = {
    "help": Message(
        content="You are already using it!",
        ephemeral=True,
    ),
    "search": Message(
        content=search_help,
        ephemeral=True,
    ),
    "xmlsearch": Message(
        embed=xml_search_help,
        ephemeral=True,
    ),
    "notes": Message(
        content="TODO add help for this (if it's really complex enough to warrant such?)",
        ephemeral=True,
    ),
    "other": Message(
        content="Anything not listed here is most likely not intended for public usage",
        ephemeral=True,
    ),
}


bp = DiscordInteractionsBlueprint()

@bp.command(
    "help",
    "Get information about this bot's commands",
    options=[
        Option(
            "command_name",
            str,
            "Name of the command to get help about",
            True,
            choices=[
                Choice(k, k)
                for k in help_messages.keys()
            ]
        )
    ],
)
def get_help(ctx: Context, command_name: str):
    return help_messages[command_name]