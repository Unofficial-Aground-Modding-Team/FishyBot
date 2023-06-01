import os
from deta_discord_interactions import DiscordInteractions

from deta_discord_interactions.utils.oauth import enable_oauth

from fishybot.blueprints.search import bp as search_bp
from fishybot.blueprints.full_search import bp as full_search_bp
from fishybot.blueprints.xml_search import bp as xml_search_bp
from fishybot.blueprints.modio import bp as modio_bp

from fishybot.blueprints.notes import blueprint as notes_bp
from fishybot.blueprints.repeater import blueprint as repeater_bp

from fishybot.help import bp as help_bp

app = DiscordInteractions()
enable_oauth(app)

app.register_blueprint(notes_bp)
app.register_blueprint(repeater_bp)
app.register_blueprint(search_bp)
app.register_blueprint(full_search_bp)
app.register_blueprint(xml_search_bp)
app.register_blueprint(modio_bp)
app.register_blueprint(help_bp)

if os.getenv("DISCORD_ADMIN_ID"):
    from fishybot.blueprints.admin import blueprint as admin_bp
    app.register_blueprint(admin_bp)
