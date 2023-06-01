from dataclasses import dataclass

from deta_discord_interactions.utils.database import (
    Database,
    LoadableDataclass,
)

from deta_discord_interactions.utils.oauth import (
    OAuthToken,
)

from fishybot.blueprints.modio.models import (
    Modio_Game,
    Modio_Mod,
)


@dataclass
class GameRecord(LoadableDataclass):
    modio_game: Modio_Game
    last_updated: int

@dataclass
class ModRecord(LoadableDataclass):
    modio_mod: Modio_Mod
    name: str
    last_updated: int

@dataclass
class ListenerRecord(LoadableDataclass):
    key: str
    webhook_oauth: OAuthToken
    last_updated: int
    disabled: bool = False

@dataclass
class ErrorRecord(LoadableDataclass):
    details: dict[str, str]

modio_games_db = Database("modio_games", record_type=GameRecord)
modio_mods_db = Database("modio_mods", record_type=ModRecord)
listeners_db = Database("modio_listeners", record_type=ListenerRecord)
errors_db = Database("modio_errors", record_type=ErrorRecord)
