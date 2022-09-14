import os

try:
    from dotenv import load_dotenv
    load_dotenv("local.env")
    print("Loaded .env file")
except ImportError:
    pass


from deta_discord_interactions import DiscordInteractions

from blueprints.cursed import bp as cursed_bp
from blueprints.search import bp as search_bp
from blueprints.full_search import bp as full_search_bp
from blueprints.xml_search import bp as xml_search_bp

from notes import blueprint as notes_bp
from help import bp as help_bp


app = DiscordInteractions()

# app.update_commands()

app.register_blueprint(cursed_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(search_bp)
app.register_blueprint(full_search_bp)
app.register_blueprint(xml_search_bp)
app.register_blueprint(help_bp)


if __name__ == '__main__':
    print("Updating commands")
    guilds = os.getenv("GUILDS")
    print(guilds)
    if guilds:
        for guild in guilds.split("&"):
            app.update_commands(guild_id=guild)
    else:
        app.update_commands()
