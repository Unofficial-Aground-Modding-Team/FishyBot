import pytest
import pathlib
import json
import requests
from unittest import mock


from deta_discord_interactions import Client, Context, Message
from deta_discord_interactions.utils.database import Database

import fishybot.blueprints.modio.modio_database as modio_db
import fishybot.blueprints.modio.operations as modio_ops

@pytest.fixture()
def blank_games_db(tmp_path):
    return Database("modio_games", record_type=modio_db.GameRecord, base_mode="DISK", base_folder=tmp_path)

@pytest.fixture()
def filled_games_db():
    # TODO: Encorce read-only?
    data_folder = pathlib.Path(__file__).parent /'data/'
    return Database("modio_games", record_type=modio_db.GameRecord, base_mode="DISK", base_folder=data_folder)

def test_game(client: Client, context: Context, blank_games_db: Database[modio_db.GameRecord], monkeypatch: pytest.MonkeyPatch):
    games_db = blank_games_db
    monkeypatch.setattr(modio_ops, "modio_games_db", games_db)
    response_data = json.load((pathlib.Path(__file__).parent /'data/game_34.json').open('r'))

    with mock.patch.object(requests, "get") as my_mock:
        my_mock().json.side_effect = lambda : response_data
        with client.context(context):
            result: Message = client.run("modio", "game", "aground")
            assert result.content is None
            assert result.embed.title == 'Aground'
            assert result.embed.description.startswith("Mods in aground use xml files")
            assert 'aground-title-promo-final' in result.embeds[0].image.url
            assert result.components is None
    
    saved = games_db["game_34"]
    assert saved.modio_game.id == 34
    assert saved.modio_game.name == 'Aground'


def test_mods(client: Client, context: Context, filled_games_db: Database[modio_db.GameRecord], monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(modio_ops, "modio_games_db", filled_games_db)

    response_data = json.load((pathlib.Path(__file__).parent /'data/game_34_mod_144.json').open('r'))
    with mock.patch.object(requests, "get") as my_mock:
        my_mock().json.side_effect = lambda : response_data
        with client.context(context):
            result1: Message = client.run("modio", "mod", "aground", "144")
            result2: Message = client.run("modio", "mod", "aground", "magic")
            assert result1 == result2
            assert result1.content is None
            assert result1.embed.title == "MagicPlus"
            assert "poly_aart" in result1.embed.footer.icon_url
            assert result1.components is None
