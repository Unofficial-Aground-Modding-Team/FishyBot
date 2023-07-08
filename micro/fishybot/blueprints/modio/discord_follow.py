import os
import requests

from deta_discord_interactions import (
    Channel,
    DiscordInteractionsBlueprint,
    Context,
    Message,
    Autocomplete,
    Option,
    Choice,
)
from deta_discord_interactions.utils.database import (
    Query,
    Field,
)
from fishybot.database.operations import (
    get_possible_games
)
from fishybot.database.sqlite_model import Game
from fishybot.blueprints.modio.modio_database import (
    ModRecord,
    modio_games_db,
    modio_mods_db,

    FollowerUser,
    discord_followers_db,
)
from fishybot.blueprints.modio.models import (
    Modio_Game,
    Modio_Mod,
)
from fishybot.blueprints.modio.operations import (
    get_game,
    get_mod,
    get_mods,
)

bp = DiscordInteractionsBlueprint()

headers = {
    "User-Agent": "Discord Bot by etrotta3846",
    "X-Modio-Platform": "Windows",
    "X-Modio-Portal": "Discord",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
}

group = bp.command_group(
    "watch",
    "Follow mod.io mods to get notified about them",
)

comments_group = group.subgroup(
    "comments",
    "Get notified when Comments are added to a mod",
)

updates_group = group.subgroup(
    "updates",
    "Get notified when a mod is Updated",
)


@comments_group.command(
    "follow",
    "If you get multiple results, try again and look for an Autocomplete suggestion.",
    annotations={
        "force_update": "If you are getting results but not the one you are after, set this to True"
    }
)
def follow_mod_comments(ctx: Context, game: Autocomplete[str], mod: Autocomplete[str], force_update: bool = False):
    if game.isdigit():
        game_record = modio_games_db.get(f'game_{game}')
        game_data = game_record.modio_game if game_record is not None else game_record
    else:
        sqlite_games: list[Game] = get_possible_games(game, include_hidden=False)
        sqlite_game: Game = next((gm for gm in sqlite_games if gm.modio_id != -1), sqlite_games[0])
        if sqlite_game.modio_id == -1:
            return Message(f"Game {sqlite_game.full_name} is not on mod.io", ephemeral=True)
        game_record = get_game(sqlite_game.modio_id)
        game_data: Modio_Game = game_record.modio_game
    if game_data is None:
        return Message("Game not found", ephemeral=True)

    mods = []
    # Try to get from Deta Base (almost like a cache)
    if mod.isdigit():
        _mod = get_mod(game_data.id, mod).modio_mod
        if _mod is not None:
            mods = [_mod]
    elif not force_update:
        mods = [
            _mod.modio_mod
            for _mod in modio_mods_db.fetch(
                Query(
                    Field("key").startswith(f"mod_{game_data.id}"),
                    Field("name").contains(mod),
                )
            )
        ]
    # If not found in Deta Base, try to get from mod.io
    if not mods:
        mods: list[Modio_Mod] = get_mods(game_data.id, {"name-lk": f"*{mod}*"}).data
    if not mods:  # If no mods were found on the database nor in mod.io
        return Message("No matching mods found", ephemeral=True)
    elif len(mods) > 1:  # If more than one mod was found on the database or in mod.io
        # TODO: Future improvement: Return a Select Menu?
        return Message(f"Multiple matching mods found: {', '.join(mod.name for mod in mods)}. \
                       Please specify one, preferably selecting the Autocomplete suggestion", ephemeral=True)
    else:  # Exactly one mod
        data = mods[0]

    mod_record = modio_mods_db.get(f"mod_{game_data.id}_{data.id}")
    if mod_record is None:
        return Message("Something went wrong", ephemeral=True)

    follower_user = discord_followers_db.get(ctx.author.id)
    if follower_user is None:
        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token:
            return Message("ERROR: The bot was not set up correctly (Missing Bot Token)", ephemeral=True)
        response = requests.post(
            "https://discord.com/api/v10/users/@me/channels",
            headers={"Authorization": f"Bot {token}", "User-Agent": "FishyBot)"},
            json={"recipient_id": ctx.author.id},
        )
        response.raise_for_status()
        channel = Channel.from_dict(response.json())
        follower_user = FollowerUser(ctx.author.id, channel.id, [data.id])
        response = requests.post(
            f"https://discord.com/api/v10/channels/{channel.id}/messages",
            headers={"Authorization": f"Bot {token}", "User-Agent": "FishyBot)"},
            json={"content": "I will now DM you through here when there are updates to mods you are watching"},
        )
        response.raise_for_status()
        discord_followers_db[ctx.author.id] = follower_user
        # NOTE: Possible race condition. Assuming that the amount of usage is gonna be small enough not to matter.
        mod_record.followers.append(channel.id)
        modio_mods_db[f"mod_{game_data.id}_{data.id}"] = mod_record
    else:
        if (data.id in follower_user.following_mods) and (follower_user.discord_dm_channel_id in mod_record.followers):
            return Message("You were already following that mod.", ephemeral=True)

        if data.id not in follower_user.following_mods:
            follower_user.following_mods.append(data.id)
            discord_followers_db[ctx.author.id] = follower_user

        if follower_user.discord_dm_channel_id not in mod_record.followers:
            mod_record.followers.append(follower_user.discord_dm_channel_id)
            modio_mods_db[f"mod_{game_data.id}_{data.id}"] = mod_record

    return Message(f"Now following the mod ``{data.name}`` comments", ephemeral=True)


@follow_mod_comments.autocomplete()
def mod_info_autocomplete(
    ctx: Context,
    game: Option = None,
    mod: Option = None,
    *_,
    **__,
):
    if game is not None and game.focused:
        games = get_possible_games(game.value, include_hidden=False)
        return [Choice(game.full_name, str(game.modio_id)) for game in games if game.modio_id != -1]
    elif mod is not None and mod.focused:
        query = []
        if game is not None and game.value.isdigit():
            query.append(Field("key").startswith(f"mod_{game.value}"))
        if mod.value != "":
            query.append(Field("name").contains(mod.value.casefold()))
        mods = modio_mods_db.fetch(Query(*query))
        mods.sort(key = lambda mod: mod.name)
        return [Choice(mod.modio_mod.name, str(mod.modio_mod.id)) for mod in mods][:25]
    return []



@comments_group.command(
    "unfollow",
    "Unfollow a mod you are currently following.",
    annotations={
        "force_update": "If you are getting results but not the one you are after, set this to True"
    }
)
def unfollow_mod_comments(ctx: Context, game: Autocomplete[str], mod: Autocomplete[str]):
    if game.isdigit():
        game_record = modio_games_db.get(f'game_{game}')
        game_data = game_record.modio_game if game_record is not None else game_record
    else:
        sqlite_games: list[Game] = get_possible_games(game, include_hidden=False)
        sqlite_game: Game = next((gm for gm in sqlite_games if gm.modio_id != -1), sqlite_games[0])
        if sqlite_game.modio_id == -1:
            return Message(f"Game {sqlite_game.full_name} is not on mod.io", ephemeral=True)
        game_record = get_game(sqlite_game.modio_id)
        game_data: Modio_Game = game_record.modio_game
    if game_data is None:
        return Message("Game not found", ephemeral=True)

    mods = []
    # Try to get from Deta Base (almost like a cache)
    if mod.isdigit():
        _mod = get_mod(game_data.id, mod).modio_mod
        if _mod is not None:
            mods = [_mod]
    else:
        mods = [
            _mod.modio_mod
            for _mod in modio_mods_db.fetch(
                Query(
                    Field("key").startswith(f"mod_{game_data.id}"),
                    Field("name").contains(mod),
                )
            )
        ]
    if not mods:  # If no mods were found on the database nor in mod.io
        return Message("No matching mods found", ephemeral=True)
    elif len(mods) > 1:  # If more than one mod was found on the database or in mod.io
        # TODO: Future improvement: Return a Select Menu?
        return Message(f"Multiple matching mods found: {', '.join(mod.name for mod in mods)}. \
                       Please specify one, preferably selecting the Autocomplete suggestion", ephemeral=True)
    else:  # Exactly one mod
        data = mods[0]

    mod_record = modio_mods_db.get(f"mod_{game_data.id}_{data.id}")
    if mod_record is None:
        return Message("Something went wrong", ephemeral=True)

    follower_user = discord_followers_db.get(ctx.author.id)
    if follower_user is None:
        return Message("You are not following any mods", ephemeral=True)

    if (data.id not in follower_user.following_mods) and (follower_user.discord_dm_channel_id not in mod_record.followers):
        return Message(f"You are not following ``{data.name}``.", ephemeral=True)

    if data.id in follower_user.following_mods:
        follower_user.following_mods.remove(data.id)
        discord_followers_db[ctx.author.id] = follower_user

    if follower_user.discord_dm_channel_id in mod_record.followers:
        mod_record.followers.remove(follower_user.discord_dm_channel_id)
        modio_mods_db[f"mod_{game_data.id}_{data.id}"] = mod_record

    return Message(f"You are no longer following the mod ``{data.name}`` comments", ephemeral=True)


@unfollow_mod_comments.autocomplete()
def mod_info_autocomplete(
    ctx: Context,
    game: Option = None,
    mod: Option = None,
    *_,
    **__,
):
    if game is not None and game.focused:
        games = get_possible_games(game.value, include_hidden=False)
        return [Choice(game.full_name, str(game.modio_id)) for game in games if game.modio_id != -1]
    elif mod is not None and mod.focused:
        query = []
        if game is not None and game.value.isdigit():
            query.append(Field("key").startswith(f"mod_{game.value}"))
        if mod.value != "":
            query.append(Field("name").contains(mod.value.casefold()))
        mods = modio_mods_db.fetch(Query(*query))
        user = discord_followers_db.get(ctx.author.id)
        if user is not None:
            def func(mod: ModRecord):
                # Ideally we would store these two on the same place and only once,
                # but with the way I am modelling the data,
                # it is *possible* for these relationships to be unsynced
                user_following_mod = user.discord_dm_channel_id in mod.followers
                mod_followed_by_user = mod.modio_mod.id in user.following_mods
                comb = user_following_mod + mod_followed_by_user
                return (
                    -3 if comb == 1 else -comb,
                    mod.name,
                )
            mods.sort(key=func)
        return [Choice(mod.modio_mod.name, str(mod.modio_mod.id)) for mod in mods][:25]
    return []


