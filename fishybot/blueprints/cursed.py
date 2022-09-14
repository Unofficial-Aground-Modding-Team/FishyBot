import random

from deta_discord_interactions import Message
# from deta_discord_interactions import Embed
# from deta_discord_interactions.models.embed import Media
from deta_discord_interactions import DiscordInteractionsBlueprint
from deta_discord_interactions.enums import PERMISSION

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