import random

from deta_discord_interactions import Message
from deta_discord_interactions import embed
# from deta_discord_interactions.models.embed import Media
from deta_discord_interactions import DiscordInteractionsBlueprint
from deta_discord_interactions.enums import PERMISSION
from deta_discord_interactions.utils import cooldown

import requests

from common.config import BOT_COLOR

bp = DiscordInteractionsBlueprint()

cursed = bp.command_group(
    "cursed",
    default_member_permissions=PERMISSION.MANAGE_MESSAGES,
)


@cursed.command(
    name="furry",
    description="Fetches a random furry from thisfursonadoesnotexist",
    annotations = dict(
        seed = "Which seed to use.",
    )
)
def furry(
    ctx,
    seed: int = None,
):
    if seed is not None:
        if isinstance(seed, str) and (len(seed) > 5 or not seed.isnumeric()):
            return Message("The seed must only contain numbers, and can only be up to 5 characters long.", ephemeral=True)
        if isinstance(seed, int) and (seed >= 100000 or seed < 0):
            return Message("The seed must be between 0 and 99999.", ephemeral=True)
    else:
        seed = random.randrange(0, 100000)
    return f"https://thisfursonadoesnotexist.com/v2/jpgs-2x/seed{seed:0>5}.jpg"


@cursed.command(
    name="waifu",
    description="Fetches a random waifu from thiswaifudoesnotexist",
    annotations = dict(
        seed = "Which seed to use.",
    )
)
def waifu(
    ctx,
    seed: int = None,
):
    if seed is not None:
        if isinstance(seed, str) and (len(seed) > 5 or not seed.isnumeric()):
            return Message("The seed must only contain numbers, and can only be up to 5 characters long.", ephemeral=True)
        if isinstance(seed, int) and (seed >= 100000 or seed < 0):
            return Message("The seed must be between 0 and 99999.", ephemeral=True)
    else:
        seed = random.randrange(0, 100000)
    return f"https://www.thiswaifudoesnotexist.net/example-{seed}.jpg"


# NOTE: Currently broken on deta, perhaps due to some IP blacklist or shared rate limit, despite working when testing locally
@cursed.command(
    name="lexica",
    description="Fetches a random image from lexica.art",
    annotations = dict(
        query = "Query to search",
    )
)
@cooldown('user', 5)
def lexica(
    ctx,
    query: str,
):
    try:
        result = requests.get("https://lexica.art/api/v1/search", {"q": query})
        images = [img for img in result.json()["images"] if not img["nsfw"]]
    except Exception as err:
        from deta_discord_interactions.utils import Database, AutoSyncRecord
        import uuid
        db = Database("_cursed_lexica_errors", record_type=AutoSyncRecord)
        with db[str(uuid.uuid4())] as record:
            record["content"] = repr(result.content)
            record["err"] = repr(err)
        print(result.content)
        raise
    if not images:
        return Message("Zero results found for that query", ephemeral=True)
    random.shuffle(images)
    priority = [
        lambda img: not img['grid'] and img['width'] <= 512 and img['height'] <= 512,
        lambda img: not img['grid'] and img['width'] <= 1024 and img['height'] <= 1024,
        lambda img: img['width'] <= 1024 and img['height'] <= 1024,
        lambda _: True,
    ]
    for condition in priority:
        image = next(filter(condition, images), None)
        if image is not None:
            break
    return Message(
        embed=embed.Embed(
            title=image["prompt"],
            url=image["gallery"],
            image=embed.Media(
                image["src"],
                None,
                image['height'],
                image['width'],
            ),
            color=BOT_COLOR,
        )
    )




# @cursed.command(
#     name="cat",
#     description="Fetches a random cat from thiscatdoesnotexists.com",
# )
# def cat(
#     ctx,
# ):
#     try:
#         return Message(embed=Embed("\N{CAT}", image=Media("https://thiscatdoesnotexist.com/"), color=0x7289da))
    
#     except Exception:
#         return Message("An unknown error occurred.", ephemeral=True)