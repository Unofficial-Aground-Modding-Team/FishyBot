import os
from deta_discord_interactions import DiscordInteractionsBlueprint, Message
from deta_discord_interactions import Context

from deta_discord_interactions.enums import PERMISSION

blueprint = DiscordInteractionsBlueprint()

@blueprint.command("eval", "internal eval command for admin usage", default_member_permissions=PERMISSION.ADMINISTRATOR)
def eval_command(ctx: Context, code: str, ephemeral: bool = True):
    "Create a repeating Webhook with a message"
    if ctx.author.id != os.getenv("DISCORD_ADMIN_ID"):
        return "You do not have the permission to use this command"
    try:
        return Message(repr(eval(code, globals(), locals())), ephemeral=ephemeral)
    except Exception as err:
        return Message(f"Got an exception: {err}", ephemeral=ephemeral)

@blueprint.command("exec", "internal exec command for admin usage", default_member_permissions=PERMISSION.ADMINISTRATOR)
def exec_command(ctx: Context, code: str, ephemeral: bool = True):
    "Create a repeating Webhook with a message"
    if ctx.author.id != os.getenv("DISCORD_ADMIN_ID"):
        return "You do not have the permission to use this command"
    message = Message("Executed successfully", ephemeral=ephemeral)
    try:
        exec(code, globals(), locals())
    except Exception as err:
        message = Message(f"Got an exception: {err}", ephemeral=ephemeral)
    return message
