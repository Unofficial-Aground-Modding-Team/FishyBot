import pytest
import os
from deta_discord_interactions import Client, Message

os.environ['DETA_SPACE_APP'] = "true"
os.environ['DETA_SPACE_APP_HOSTNAME'] = "https://example-1-a1234567.deta.app/"

def test_register(client: Client):
    msg: Message = client.run("repeat", "register", "test123", "Hello World!")
    assert msg.content is not None

# TODO ADD MORE TESTS