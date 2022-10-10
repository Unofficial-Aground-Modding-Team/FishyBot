from main import app
from deta_discord_interactions import Client
from deta_discord_interactions import Context
from deta_discord_interactions.models import User

client = Client(app)

commands = [
    # ("cursed", "furry"),
    # ("cursed", "waifu"),
    # ("cursed", "lexica", "bird"),

    # ("search", "aground", "item", "wyrm"),
    # ("search", "aground", "item", "wyrm@mod@core"),
    # ("fullsearch", "aground", "item", "wyrm"),

    # ("xmlsearch", "aground", "item", """[@attack]"""),
    # ("xmlsearch", "aground", "item", """[@cost="0"]"""),
    # ("xmlsearch", "aground", "recipe", """[@type="magic_forge"]"""),

    # ("xmlsearch", "aground", "item", """.//stat"""),
    # ("xmlsearch", "aground", "object", """.//addedToArea"""),
    # ("xmlsearch", "aground", "item", """stat[@time]"""),
    # ("xmlsearch", "aground", "item", """stat[@max]"""),

    # ("help", "help"),
    # ("help", "search"),
    # ("help", "xmlsearch"),
    # ("help", "notes"),
    # ("help", "other"),

    # ("modio", "game", "aground"),
    # ("modio", "game", "34"),

    # ("modio", "mod", "aground", "magic"),
    # ("modio", "mod", "aground", "magic", True),
    # ("modio", "mod", "aground", "144"),
    # ("modio", "mod", "aground", "aster"),
    # ("modio", "mod", "aground", "plus", True),

    # ("comments", "check"),
    # ("comments", "run"),
]

handlers = [
    # ("select_data", "wyrm@item@aground"),
    # ("select_data", "nuke_blast@object@full@aground"),
]

autocompletes = [
    # ("search", "agro"),
    # ("search", "aground", "it"),
    # ("search", "aground", "item", ""),
    # ("search", "aground", "item", "wy"),
    # ("search", "aground", "item", ""),
    # ("search", "aground", ""),
    
    # ("search", "stardander_revenant", ""),
    # ("search", "stardander_demo", ""),
    
    # ("xmlsearch", ""),

    # ("modio", "mod", "34", "magic"),
    # ("modio", "mod", "aground", "magic"),
    # ("modio", "mod", "aground", ""),
    # ("modio", "mod", "34", ""),
]

with open("test.log", 'a') as file:
    for command in commands:
        ctx = Context(
            guild_id="903078036272975922",
            channel_id="903078036272975925",
            author=User("256442550683041793", "etrotta"),
        )
        with client.context(ctx):
            test = client.run(*command)
            print(command, test, end='\n\n')
            print(command, test, sep='\n', end='\n\n', file=file)

    for handler_id, value in handlers:
        ctx = Context(values=[value])
        with client.context(ctx):
            test = client.run_handler(handler_id)
            print((handler_id, value), test, end='\n\n')
            print((handler_id, value), test, sep='\n', end='\n\n', file=file)

    for autocomplete in autocompletes:
        test = client.run_autocomplete(*autocomplete)
        print(autocomplete, test, end='\n\n')
        print(autocomplete, test, sep='\n', end='\n\n', file=file)
        print(len(test.choices))
