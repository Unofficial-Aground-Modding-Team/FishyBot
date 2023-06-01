from deta_discord_interactions import Client, Context, Message

def test_help(client: Client, context: Context):
    with client.context(context):
        result: Message = client.run("help", "help")
        assert result.content == "You are already using it!"
        assert result.embed is None
        result: Message = client.run("help", "xmlsearch")
        assert result.content is None
        assert result.embed is not None
