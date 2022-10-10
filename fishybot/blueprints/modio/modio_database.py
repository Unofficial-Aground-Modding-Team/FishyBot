from dataclasses import dataclass

from deta_discord_interactions.utils.database import (
    Database,
    Record,
    AutoSyncRecord,
)

from deta_discord_interactions.utils.oauth import (
    OAuthToken,
)

from blueprints.modio.models import (
    Modio_Game,
    Modio_Mod,
)


@dataclass
class GameRecord(Record):
    modio_game: Modio_Game = None
    last_updated: int = None

@dataclass
class ModRecord(Record):
    modio_mod: Modio_Mod = None
    name: str = None
    last_updated: int = None

@dataclass
class ListenerRecord(Record):
    key: str = None
    webhook_oauth: OAuthToken = None
    last_updated: int = None
    disabled: bool = False


modio_games_db = Database("modio_games", record_type=GameRecord)
modio_mods_db = Database("modio_mods", record_type=ModRecord)
listeners_db = Database("modio_listeners", record_type=ListenerRecord)
errors_db = Database("modio_errors", record_type=AutoSyncRecord)
