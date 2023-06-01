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

print("Updating commands")
guilds = os.getenv("GUILDS")
print(guilds)

if guilds:
    for guild in guilds.split("&"):
        print(f"Updating commands for guild {guild}")
        app.update_commands(guild_id=guild)
else:
    app.update_commands()
