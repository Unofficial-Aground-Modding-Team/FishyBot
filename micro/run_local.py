import os
import pathlib

# You might want to consider using python-dotenv instead
env = pathlib.Path(__file__).parent / '.env'
if env.is_file():
    with env.open('r') as file:
        for line in file:
            try:
                k, v = line.strip().split("=")
                os.environ[k] = v
            except Exception:
                pass
            

from fishybot.main import app

from deta_discord_interactions.http import run_server

run_server(app)
