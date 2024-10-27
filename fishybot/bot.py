from pathlib import Path

import discord
from discord import app_commands
import discord.ext.commands as commands

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

class FishyBot(commands.Bot):
    def __init__(
            self,
            database_connection: async_sessionmaker[AsyncSession]
        ):
        super().__init__(
            command_prefix=commands.when_mentioned_or("$"),
            description="Bot created by etrotta",
            intents=discord.Intents.all(),
            allowed_contexts=app_commands.AppCommandContext(
                guild=True,
                dm_channel=True,
                private_channel=True,
            ),
            allowed_installs=app_commands.AppInstallationType(
                guild=False,
                user=True,
            ),
        )
        self.allowed_mentions = discord.AllowedMentions.none()
        self.cogs_dir = Path(__file__).parent / "cogs"
        self.database_connection = database_connection

    async def load_extensions(self):
        for file in self.cogs_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            try:
                rel = file.relative_to(Path.cwd())
                await self.load_extension(".".join(rel.with_suffix("").parts))
                print(f"Loaded {rel}")
            except commands.ExtensionError as e:
                print(f"Failed to load {file}: {e}")
