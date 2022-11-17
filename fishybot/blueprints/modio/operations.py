import os
import time
from typing import Optional

import requests

from blueprints.modio.models import (
    Modio_Game,
    Modio_Mod,
    Modio_Comment,
    # Modio_Event,
    Modio_Mods,
    Modio_Events,
    Modio_Comments,
)
from blueprints.modio.modio_database import (
    modio_games_db,
    modio_mods_db,
    GameRecord,
    ModRecord
)



headers = {
    "User-Agent": "Discord Bot by etrotta3846",
    "X-Modio-Platform": "Windows",
    "X-Modio-Portal": "Discord",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
}

BASE_URL = "https://api.mod.io/v1"


def get_game(game_id: int, force_update: bool = False) -> GameRecord:
    if game_id == -1:
        raise Exception()
    if not force_update:
        record = modio_games_db.get(f'game_{game_id}')
    if force_update or record.modio_game is None:
        last_updated = int(time.time())
        response = requests.get(
            BASE_URL + f"/games/{game_id}",
            headers=headers,
            params={"api_key": os.getenv("MODIO_API_KEY")}
        )
        response.raise_for_status()
        modio_game = Modio_Game.from_dict(response.json())
        record = GameRecord(modio_game=modio_game, last_updated=last_updated)
        modio_games_db[f'game_{game_id}'] = record
    return record


def get_mod(game_id: int, mod_id: int, force_update: bool = False) -> ModRecord:
    if not force_update:
        record = modio_mods_db.get(f'mod_{game_id}_{mod_id}')
    if force_update or record is None or record.modio_mod is None:
        last_updated = int(time.time())
        response = requests.get(
            BASE_URL + f"/games/{game_id}/mods/{mod_id}",
            headers=headers,
            params={"api_key": os.getenv("MODIO_API_KEY")}
        )
        response.raise_for_status()
        modio_mod = Modio_Mod.from_dict(response.json())
        record = ModRecord(modio_mod=modio_mod, last_updated=last_updated, name=modio_mod.name.casefold())
        modio_mods_db[f'mod_{game_id}_{mod_id}'] = record
    return record


def get_mods(game_id: int, filters: dict[str, str]) -> Modio_Mods:
    "See https://docs.mod.io/#filtering for the filters"
    if game_id == -1:
        raise Exception()
    last_updated = int(time.time())
    response = requests.get(
        BASE_URL + f"/games/{game_id}/mods",
        headers=headers,
        params={"api_key": os.getenv("MODIO_API_KEY"), **filters}
    )
    response.raise_for_status()
    mods = Modio_Mods.from_dict(response.json())
    records = []
    for mod in mods.data:
        record = ModRecord(modio_mod=mod, last_updated=last_updated, name=mod.name.casefold())
        records.append(record)
    modio_mods_db.put_many(
        records,
        key_source = lambda mod_record: f'mod_{game_id}_{mod_record.modio_mod.id}',
    )
    return mods


def get_comment(game_id: int, mod_id: int, comment_id: int) -> Modio_Comment:
    response = requests.get(
        BASE_URL + f"/games/{game_id}/mods/{mod_id}/comments/{comment_id}",
        headers=headers,
        params={"api_key": os.getenv("MODIO_API_KEY")},
    )
    response.raise_for_status()
    return Modio_Comment.from_dict(response.json())


def get_comments(game_id: int, mod_id: int, filters: dict[str, str]) -> Modio_Comments:
    response = requests.get(
        BASE_URL + f"/games/{game_id}/mods/{mod_id}/comments",
        headers=headers,
        params={"api_key": os.getenv("MODIO_API_KEY"), **filters},
    )
    response.raise_for_status()
    return Modio_Comments.from_dict(response.json())


def get_events(game_id: int, mod_id: Optional[int] = None, filters: dict[str, str] = {}) -> Modio_Events:
    if mod_id is not None:
        url = BASE_URL + f"/games/{game_id}/mods/{mod_id}/events"
    else:
        url = BASE_URL + f"/games/{game_id}/mods/events"

    response = requests.get(
        url,
        headers=headers,
        params={"api_key": os.getenv("MODIO_API_KEY"), **filters},
    )
    response.raise_for_status()
    return Modio_Events.from_dict(response.json())
