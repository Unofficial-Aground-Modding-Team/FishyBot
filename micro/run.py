from fishybot.main import app

from deta_discord_interactions.http import run_server

run_server(app)
