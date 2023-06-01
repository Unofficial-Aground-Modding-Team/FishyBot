import pathlib
import pytest
import json
from unittest import mock
import requests

from deta_discord_interactions import DiscordInteractions, Client, Message
from deta_discord_interactions.utils.database import Database

from deta_discord_interactions.utils.oauth import Webhook

import fishybot.blueprints.modio.modio_database as modio_db
import fishybot.blueprints.modio.operations as modio_ops
import fishybot.blueprints.modio.blueprint as modio_bp

def test_ensure_registered(app: DiscordInteractions):
    # assert sorted(app.deta_actions.keys()) == ["check_comments"]
    assert "check_comments" in app.deta_actions.keys()


data_folder = pathlib.Path(__file__).parent /'data/'
# TODO: Encorce read-only?
@pytest.fixture()
def filled_listeners_db():
    # Right now it is updating the time on the listener, which despite not being way too big of a deal, is not ideal
    return Database("modio_listeners", record_type=modio_db.ListenerRecord, base_mode="DISK", base_folder=data_folder)
@pytest.fixture()
def filled_games_db():
    return Database("modio_games", record_type=modio_db.GameRecord, base_mode="DISK", base_folder=data_folder)
@pytest.fixture()
def filled_mods_db():
    return Database("modio_mods", record_type=modio_db.ModRecord, base_mode="DISK", base_folder=data_folder)


# I probably should break it down into smaller parts? eh... whatever
# holy * this test feels so wrong in so many levels
# ALSO TODO TEST REPLIES X-X
def test_comments(
        client: Client,
        monkeypatch: pytest.MonkeyPatch,
        filled_listeners_db: Database[modio_db.ListenerRecord],
        filled_games_db: Database[modio_db.GameRecord],
        filled_mods_db: Database[modio_db.ModRecord],
    ):
    # -----------
    monkeypatch.setattr(modio_bp, "listeners_db", filled_listeners_db)
    monkeypatch.setattr(modio_bp, "modio_games_db", filled_games_db)
    monkeypatch.setattr(modio_ops, "modio_games_db", filled_games_db)
    monkeypatch.setattr(modio_bp, "modio_mods_db", filled_mods_db)
    monkeypatch.setattr(modio_ops, "modio_mods_db", filled_mods_db)
    # -----------
    files = iter([
        'game_34_mod_144_events.json',
        'game_34_mod_144_comments.json',
    ])
    def response_data():
        file = next(files)
        data = json.load((pathlib.Path(__file__).parent /f'data/{file}').open('r'))
        return data
    with (
        mock.patch.object(requests, "get") as requests_mock,
        mock.patch.object(Webhook, "send") as webhook_mock,
    ):
        requests_mock().json.side_effect = response_data
        client.run_action("check_comments")
        webhook_mock.assert_called_once()
        msg: Message = webhook_mock.call_args[0][0]
        assert isinstance(msg, Message)
        assert msg.content is None
        assert msg.embeds is not None
        assert msg.embeds[0].title == "New comments in MagicPlus"
        assert "test_commenter" in msg.embeds[0].description
        assert "Fake test comment." in msg.embeds[0].description
        assert msg.components is None
