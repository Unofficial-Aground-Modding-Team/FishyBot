import copy
from deta_discord_interactions import ActionRow, Client, Context, Embed, Message, SelectMenu

def test_basic_search(client: Client, context: Context):
    with client.context(context):
        result: Message = client.run("search", "aground", "item", "wyrm")
        assert result.content is None
        assert isinstance(result.embed, Embed)
        assert result.embed.title == "Select which item you want to see:"
        assert isinstance(result.components[0], ActionRow)
        select_menu: SelectMenu = result.components[0].components[0]
        assert isinstance(select_menu, SelectMenu)
        assert select_menu.custom_id == "select_data"
        assert select_menu.values is None
        assert len(select_menu.options) == 8
        select_menu.options.sort(key=lambda opt: opt.label)
        assert select_menu.options[0].label == "magic_wyrm"
        assert select_menu.options[4].label == "wyrm"
        assert select_menu.options[4].value == "wyrm@item@core@aground"
        assert select_menu.options[7].label == "wyrm_queen"
        assert select_menu.options[0].value == "magic_wyrm@item@full@aground"

        result: Message = client.run("search", "aground", "item", "wyrm@mod@core")
        assert result.content.startswith('''```xml\n<item id="wyrm''')

        result: Message = client.run("fullsearch", "aground", "item", "wyrm")
        assert result.components is not None 
        assert isinstance(result.components[0], ActionRow)
        assert isinstance(result.components[0].components[0], SelectMenu)
        has_minigames = False
        has_magicplus = False
        for opt in result.components[0].components[0].options:
            if "magicplus" in opt.description.casefold():
                has_magicplus = True
            if "minigames" in opt.description.casefold():
                has_minigames = True
        assert has_minigames and has_magicplus


def test_xml_search(client: Client, context: Context):
    with client.context(context):
        result: Message = client.run("xmlsearch", "aground", "item", """[@attack]""")
        assert result.content is None
        assert result.embed.title == "Select which item you want to see:"
        select_menu = result.components[0].components[0]
        assert isinstance(select_menu, SelectMenu)
        assert len(select_menu.options) == 25

        for category, query in [
            ('item', '[@cost="0"]'),
            ('recipe', '[@type="magic_forge"]'),
            ("object", './/addedToArea'),
            ("item", 'stat[@time]'),
        ]:
            result: Message = client.run("xmlsearch", "aground", category, query)
            assert result.content is None
            assert result.embed.title == f"Select which {category} you want to see:"
            select_menu = result.components[0].components[0]
            assert isinstance(select_menu, SelectMenu)
            assert len(select_menu.options) > 0

def test_search_handlers(client: Client, context: Context):
    ctx = copy.copy(context)
    ctx.values = ["wyrm@item@core@aground"]
    with client.context(ctx):
        with client.context(ctx):
            result: Message = client.run_handler("select_data")
            assert result.content.startswith('```xml\n<item id="wyrm"')
    ctx.values = ["nuke_blast@object@full@aground"]
    with client.context(ctx):
        with client.context(ctx):
            result: Message = client.run_handler("select_data")
            assert result.content.startswith('```xml\n<object id="nuke_blast"')


def test_search_autocomplete(client: Client, context: Context):
    with client.context(context):
        result = client.run_autocomplete("search", "agro")
        # TODO May have to update if/once I add Aground Zero
        assert len(result.choices) == 1 and result.choices[0]["value"] == "aground"
        for query in [
            ("search", "aground", ""),
            ("search", "aground", "it"),
            ("search", "aground", "item", ""),
            ("search", "aground", "item", "wy"),
            ("search", "aground", "quest", "bombard"),
            ("xmlsearch", ""),
        ]:
            result = client.run_autocomplete(*query)
            assert len(result.choices) > 1
