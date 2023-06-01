import os
import pytest

os.environ["DONT_REGISTER_WITH_DISCORD"] = "True"
os.environ["DONT_VALIDATE_SIGNATURE"] = "True"

os.environ["DISCORD_CLIENT_ID"] = "123"
os.environ["DISCORD_PUBLIC_KEY"] = "123"
os.environ["DISCORD_CLIENT_SECRET"] = "123"

os.environ["DETA_ORM_DATABASE_MODE"] = "MEMORY"
os.environ["DETA_ORM_FORMAT_NICELY"] = "1"
os.environ["DETA_PROJECT_KEY"] = ""

os.environ["GUILDS"] = "903078036272975922&422847864172183562"

os.environ["MODIO_API_KEY"] = ""

from deta_discord_interactions import User, Client, Context
from fishybot.main import app as main_app

@pytest.fixture(scope="module")
def app():
    return main_app

@pytest.fixture(scope="module")
def client(app):
    return Client(app)

@pytest.fixture(scope="module")
def context():
    return Context(
        guild_id="903078036272975922",
        channel_id="903078036272975925",
        author=User("256442550683041793", "etrotta"),
    )


@pytest.fixture(autouse=True)
def no_http_requests(monkeypatch):
    def urlopen_mock(self, method, url, *args, **kwargs):
        raise RuntimeError(
            f"The test was about to {method} {self.scheme}://{self.host}{url}"
        )

    monkeypatch.setattr(
        "urllib3.connectionpool.HTTPConnectionPool.urlopen", urlopen_mock
    )
