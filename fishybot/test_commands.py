from main import app
from deta_discord_interactions import Client
from deta_discord_interactions import Context

client = Client(app)

commands = [
    # ("cursed", "furry"),
    # ("cursed", "waifu"),

    # ("search", "aground", "item", "wyrm"),
    # ("search", "aground", "item"),

    # ("xmlsearch", "aground", "item", """[@attack]"""),
    # ("xmlsearch", "aground", "item", """[@cost="0"]"""),
    # ("xmlsearch", "aground", "recipe", """[@type="magic_forge"]"""),

    # ("xmlsearch", "aground", "item", """.//stat"""),
    # ("xmlsearch", "aground", "item", """stat[@time]"""),
    # ("xmlsearch", "aground", "item", """stat[@max]"""),

    # ("help", "help"),
    # ("help", "search"),
    # ("help", "xmlsearch"),
    # ("help", "notes"),
    # ("help", "other"),
]

handlers = [
    # ("select_data", "wyrm@item@aground"),
]

autocompletes = [
    # ("search", "agro"),
    # ("search", "aground", "it"),
    # ("search", "aground", "item", ""),
    # ("search", "aground", "item", "wy"),
    # ("search", "aground", "item", ""),
    # ("search", "aground", ""),
    
    # ("fullsearch", "aground_zero", ""),
    
    ("xmlsearch", ""),
]

with open("test.log", 'w') as file:
    for command in commands:
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
