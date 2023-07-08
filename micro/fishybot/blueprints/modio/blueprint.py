from datetime import datetime
import json
import math
import os
import time
import uuid
import requests

from deta_discord_interactions import (
    # DiscordInteractionsBlueprint,
    Context,
    Message,
    Embed,
    embed,
    Autocomplete,
    Option,
    Choice,
)
from deta_discord_interactions.enums.permissions import PERMISSION
from deta_discord_interactions.utils.oauth import (
    OAuthToken,
    create_webhook,
    remember_callback,
)
from deta_discord_interactions.utils.database import (
    Query,
    Field,
)

from fishybot.common.config import BOT_COLOR
from fishybot.database.operations import (
    get_possible_games
)
from fishybot.database.sqlite_model import Game
from fishybot.blueprints.modio.modio_database import (
    ListenerRecord,
    listeners_db,
    ErrorRecord,
    errors_db,
    modio_games_db,
    modio_mods_db,
)
from fishybot.blueprints.modio.models import (
    Modio_Game,
    Modio_Mod,
    Modio_Comment,
    Modio_Comments,
    Modio_Events,
)
from fishybot.blueprints.modio.operations import (
    get_game,
    get_mod,
    get_mods,
    get_comment,
    get_events,
    get_comments,
)

# seems like register() was only implemented for the DiscordInteractions, not for bps
# just building on top of it works though I guess
from fishybot.blueprints.modio.discord_follow import bp

headers = {
    "User-Agent": "Discord Bot by etrotta",
    "X-Modio-Platform": "Windows",
    "X-Modio-Portal": "Discord",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
}

group = bp.command_group(
    "modio",
    "Retrieve data from mod.io",
)

# INFO COMMANDS

@group.command("game")
def game_info(ctx: Context, game: Autocomplete[str]):
    data = None
    if game.isdigit():
        game_record = get_game(game)
        assert game_record is not None
        data: Modio_Game = game_record.modio_game
    else:
        sqlite_games: list[Game] = get_possible_games(game, include_hidden=False)
        sqlite_game: Game = next((gm for gm in sqlite_games if gm.modio_id != -1), sqlite_games[0])
        if sqlite_game.modio_id == -1:
            return Message(f"Game {sqlite_game.full_name} is not on mod.io", ephemeral=True)
        game_record = get_game(sqlite_game.modio_id)
        data: Modio_Game = game_record.modio_game

    if data is None:
        return Message("Game not found", ephemeral=True)

    return Message(
        embed=Embed(
            title=data.name,
            description=data.summary,
            url=data.profile_url,
            timestamp=datetime.fromtimestamp(data.date_live).isoformat(),
            image=embed.Media(
                url=data.logo.thumb_640x360,
            ),
            color=BOT_COLOR,
        ),
        ephemeral=True,
    )

@game_info.autocomplete()
def game_info_autocomplete(
    ctx: Context,
    game: Option = None
):
    if game is not None and game.focused:
        games = get_possible_games(game.value, include_hidden=False)
        return [Choice(game.full_name, str(game.modio_id)) for game in games if game.modio_id != -1]
    return []


@group.command(
    "mod",
    "If you get multiple results, try again and look for an Autocomplete suggestion.",
    annotations={
        "force_update": "If you are getting results but not the one you are after, set this to True"
    }
)
def mod_info(ctx: Context, game: Autocomplete[str], mod: Autocomplete[str], force_update: bool = False):
    if game.isdigit():
        game_record = modio_games_db.get(f'game_{game}')
        assert game_record is not None
        game_data = game_record.modio_game
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
        return Message(f"Multiple matching mods found: {', '.join(mod.name for mod in mods)}", ephemeral=True)
    else:  # Exactly one mod
        data = mods[0]

    return Message(
        embed=Embed(
            title=data.name,
            description=data.summary,
            url=data.profile_url,
            timestamp=datetime.fromtimestamp(data.date_live).isoformat(),
            image=embed.Media(
                url=data.logo.thumb_640x360,
            ),
            footer=embed.Footer(
                text=data.submitted_by.display_name_portal or data.submitted_by.username,
                icon_url=data.submitted_by.avatar.thumb_50x50,
            ),
            author=embed.Author(
                name=game_data.name,
                url=game_data.profile_url,
                icon_url=game_data.icon.thumb_64x64,
            ),
            color=BOT_COLOR,
        ),
        ephemeral=True,
    )


@mod_info.autocomplete()
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
        return [Choice(mod.modio_mod.name, str(mod.modio_mod.id)) for mod in mods]
    return []

# COMMENTS TASK

comment_commands = bp.command_group(
    "comments",
    "Manage the Comment watching part. For most part just leave this to etrotta.",
    default_member_permissions=PERMISSION.MANAGE_WEBHOOKS,
    dm_permission=False,
)

@remember_callback
def _save_listener(oauth_token: OAuthToken, ctx: Context):
    if oauth_token is None:
        return "Something went wrong"
    listeners_db[ctx.guild_id] = ListenerRecord(ctx.guild_id, oauth_token, int(time.time()), False)
    return f"Saved Listener for guild {ctx.guild_id}"

@comment_commands.command("setup")
def register_listener(ctx: Context):
    return create_webhook(ctx, internal_id=ctx.guild_id, callback=_save_listener)

@comment_commands.command("check")
def check_listener(ctx: Context):
    record = listeners_db.get(ctx.guild_id)
    if record is None:
        return Message(f"No Listener found for this server", ephemeral=True)
    return Message(f"Enabled: {not record.disabled}, Last Updated: <t:{record.last_updated}>", ephemeral=True)

@comment_commands.command("logs")
def get_errors(ctx: Context, limit: int = 10):
    "Returns the `limit` most recent errors. Does not filters by Listener."
    errors = errors_db.fetch(limit=limit)
    if not errors:
        return Message("No errors found.", ephemeral=True)
    return Message('\n'.join(json.dumps(err.to_dict()) for err in errors), ephemeral=True)


# Games -> Events -> Mod comments -> ?Comment Replies to

def handle_error(listener: ListenerRecord, reason: str, error):
    listener.disabled = True
    listeners_db[listener.key] = listener
    errors_db.put(str(uuid.uuid4()), ErrorRecord({"reason": reason, "error": error, "listener": listener.key}))
    try:
        listener.webhook_oauth.webhook.send(Message("An error happened, pls fix <@256442550683041793> - automatically disabling this listener."))
    except Exception:
        print("Failed to report error to webhook")
        raise
    raise Exception("Something went wrong")


def get_games() -> list[Modio_Game]:
    # You may need to use `/modio game ...` to update the database first
    return [game_record.modio_game for game_record in modio_games_db.fetch()]


def get_events_from_game(game: Modio_Game, listener: ListenerRecord) -> Modio_Events:
    date_added_min = listener.last_updated
    filters = {
        "_limit": 10,
        "date_added-min": date_added_min,
        "event_type": "MOD_COMMENT_ADDED"
    }
    errors = []
    for _ in range(3):
        try:
            events = get_events(game.id, None, filters)
            break
        except Exception as err:
            errors.append(err)
    else:
        handle_error(listener, "modio triple error at events from game", str(errors))
    return events


def get_mods_from_events(game: Modio_Game, events: Modio_Events) -> list[Modio_Mod]:
    mod_ids = {event.mod_id for event in events.data}
    mods = []
    for mod_id in mod_ids:
        mods.append(get_mod(game.id, mod_id, force_update=False).modio_mod)
    return mods

def get_comments_from_mod(game: Modio_Game, mod: Modio_Mod, listener: ListenerRecord) -> Modio_Comments:
    filters = {
        "_limit": 10,
        "date_added-min": listener.last_updated,
    }
    return get_comments(game.id, mod.id, filters)

def get_reply_origins_from_comment(game: Modio_Game, mod: Modio_Mod, comment: Modio_Comment, listener: ListenerRecord) -> list[Modio_Comment]:
    "If a comment is a Reply, fetch the comments it is replying to."
    source = []
    while comment.reply_id:  # != 0 and is not None
        comment = get_comment(game.id, mod.id, comment.reply_id)
        source.append(comment)
    return source[::-1]

# TODO use treading if the execution time becomes an issue

@bp.action("check_comments")
def get_new_comments(*_):
    NEW_LAST_UPDATED = math.floor(time.time())
    listeners = listeners_db.fetch(Query(Field("disabled") == False))
    if not listeners:
        print("No active listeners")
        return
    listener = listeners[0]

    embeds = []
    for game in get_games():
        events = get_events_from_game(game, listener)
        for mod in get_mods_from_events(game, events):
            description = []
            comment: Modio_Comment
            # TODO: Consider getting all comments at once instead of getting the reply source multiple times
            for comment in get_comments_from_mod(game, mod, listener).data:

                _reply_indent = 0
                for reply in get_reply_origins_from_comment(game, mod, comment, listener):
                    description.append(
                        (_reply_indent * ".") + 
                        f"""In response to **{reply.user.display_name_portal or reply.user.username}**"""
                        f""" saying: {reply.content.strip()}\n"""
                    )
                    _reply_indent += 4

                description.append(
                    (_reply_indent * ".") + 
                    f"""**{comment.user.display_name_portal or comment.user.username}**"""
                    f""" said: {comment.content.strip()}\n"""
                )

            embed_ = Embed(
                title=f"New comments in {mod.name}",
                url=mod.profile_url,
                description="\n".join(description),
                author=embed.Author(
                    name=game.name,
                    url=game.profile_url,
                    icon_url=game.icon.thumb_128x128,
                ),
                footer=embed.Footer(
                    text=mod.submitted_by.display_name_portal or mod.submitted_by.username,
                    icon_url=mod.submitted_by.avatar.thumb_50x50,
                ),
                color=BOT_COLOR,
            )
            embeds.append(embed_)

            # TODO ASYNC OR THREADING THIS?
            # Out of everything that won't scale with my current approach to the Watcher stuff,
            # this bit is the one that will scale the worst of all
            mod_record = modio_mods_db.get(f"mod_{game.id}_{mod.id}")
            if mod_record is None:  # might wanna save it here? if it even can be None...
                continue
            token = os.getenv("DISCORD_BOT_TOKEN")
            for listener_channel in mod_record.followers:
                if token is None:
                    print(f"Tried to DM {listener_channel} but the Token is not set")
                else:
                    response = requests.post(
                        f"https://discord.com/api/v10/channels/{listener_channel}/messages",
                        headers={"Authorization": f"Bot {token}", "User-Agent": "FishyBot)"},
                        json={"embeds": [embed_.dump()]},
                    )
                    if not (200 <= response.status_code < 300):
                        print(f"Got a non 2xx response DMing {listener_channel}: {response.status_code} {response.content}")
                        token = None  # Minimal protection to avoid worsening things in case we hit a rate limit or something
                        # TODO CHECK IF THE USER BLOCKED THE BOT?

    if not embeds:
        return

    message = Message(embeds=embeds, allowed_mentions={"parse": []})

    for listener in listeners:
        try:
            listener.webhook_oauth.webhook.send(message)
            listener.last_updated = NEW_LAST_UPDATED
            print("Sent comments to webhook")
        except Exception as err:
            listener.disabled = True
            errors_db.put(str(uuid.uuid4()), ErrorRecord({"reason": "webhook failed to send", "listener": listener.key, "error": str(err)}))
            print("Failed to send to webhook")
        listeners_db[listener.key] = listener
