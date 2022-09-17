# File literally copy-pasted from the example bot

from deta_discord_interactions import (
    DiscordInteractionsBlueprint,
    Context,

    Modal,
    ActionRow,
    TextInput,
    TextStyles,

    Message,
    SelectMenu,
    SelectMenuOption,

    Autocomplete,
    Option,
    Choice,

    ApplicationCommandType,
)
from deta_discord_interactions.utils import Database

# kwarg to pass to all non-ephemeral Messages that might contain user inputted text
no_mentions = {"allowed_mentions": {"parse": []}}

blueprint = DiscordInteractionsBlueprint()
database = Database()
def modal(name: str, description: str) -> Modal:
    return Modal(
        "create_note_modal",
        "Create or edit a note",
        [
            ActionRow(
                [TextInput("note_name", "Name", value=name)],
            ),
            ActionRow(
                [TextInput("note_description", "Description", style=TextStyles.PARAGRAPH, value=description)],
            ),
        ]
    )

notes = blueprint.command_group("notes", "Create and manage your notes")


@notes.command("create", "Add a new note to your collection.")
def add_note(ctx: Context, name: str, description: str):
    user = database[ctx.author]
    user_notes = user.setdefault("notes", {})
    if name in user_notes:
        return Message(f"Note {name} already exists, use `/notes update` or `/notes set` if you want to change it", ephemeral=True)
    user_notes[name] = description
    return Message(f"Registered note {name}", ephemeral=True)


@notes.command("modal", "Opens a model for you to add or edit a note.")
def note_modal(ctx: Context, name: Autocomplete[str] = ''):
    if name:
        user = database[ctx.author]
        user_notes = user.setdefault("notes", {})
        return modal(name, user_notes.get(name, ''))
    else:
        return modal('', '')


@blueprint.command("Save as note", "Save this message as a note.", type=ApplicationCommandType.MESSAGE)
def message_to_note(ctx: Context, message: Message):
    if len(message.content) > 4000:
        return Message("This message is too long to save as a note!", ephemeral=True)
    return modal('', message.content)


@blueprint.custom_handler("create_note_modal")
def save_modal_note(ctx: Context):
    user = database[ctx.author]
    user_notes = user.setdefault("notes", {})
    name = ctx.get_component("note_name").value
    is_update = name in user_notes
    description = ctx.get_component("note_description").value
    user_notes[name] = description
    if is_update:
        return Message(f"Updated note {name}", ephemeral=True)
    else:
        return Message(f"Registered note {name}", ephemeral=True)


@notes.command("get", "Retrieve a note from collection.")
def get_note(ctx: Context, name: Autocomplete[str], ephemeral: bool = True):
    user = database[ctx.author]
    return Message(
        user.setdefault("notes", {}).get(name, f"Note {name} not found"),
        ephemeral=ephemeral,
        **no_mentions,
    )


@notes.command("list", "List and preview all notes from your collection. If not ephemeral, anyone can see them.",
    annotations={
        "ephemeral": "Send an ephemeral message. Otherwise, uses a Select Menu if you have up to 25 notes.",
        "preview": "Include the start of each note."
    }
)
def list_notes(ctx: Context, ephemeral: bool = False, preview: bool = True):
    user = database[ctx.author]
    user_notes = user.setdefault("notes", {})

    if ephemeral or len(user_notes) > 25:
        if preview:
            result = "\n".join(
                f"{key}: {description if len(description) < 100 else description[:97]+'...'}"
                for key, description in user_notes.items()
            )
            if len(result) > 1950:
                result = "The result would be too long to display with `preview=True`!"
            else:
                result = '```' + result + '```'
        else:
            result = "```\n" + ", ".join(user_notes.keys()) + "```"
        return Message(result, ephemeral=ephemeral, **no_mentions)
    else:
        options = []
        for name, description in user_notes.items():
            if len(description) > 100:
                description = (description)[:97] + "..."
            options.append(
                SelectMenuOption(name, name, description if preview else None),
            )
        return Message("Select a note to see it:", components=[ActionRow([SelectMenu("notes_list", options)])])


@blueprint.custom_handler("notes_list")
def show_full_note(ctx: Context):
    if ctx.author.id != ctx.message.interaction.user.id:
        return Message(
            "Those are not your notes!",
            ephemeral=True,
        )
    name = ctx.values[0]
    return Message(
        database[ctx.author]["notes"][name],
        ephemeral=True,
    )
    # NOTE: Add buttons later?
    # Actually can you even add them to an ephemeral message?


@notes.command("update")
def update_note(ctx: Context, name: Autocomplete[str], description: str):
    "Updates an existing note"
    user = database[ctx.author]
    user_notes = user.setdefault("notes", {})
    if name not in user_notes:
        return Message(f"Note {name} not found. Use `/note create` or `/note set` to add a new one", ephemeral=True)
    elif user_notes[name] == description:
        return Message(f"Note {name} was already set to that", ephemeral=True)
    else:
        user_notes[name] = description
        return Message(f"Note {name} updated", ephemeral=True)


@notes.command("set")
def set_note(ctx: Context, name: Autocomplete[str], description: str):
    "Update an existing note or create a new one"
    user = database[ctx.author]
    user_notes = user.setdefault("notes", {})
    is_update = name in user_notes
    user_notes[name] = description
    if is_update:
        return Message(f"Note {name} updated", ephemeral=True)
    else:
        return Message(f"Note {name} registered", ephemeral=True)


@notes.command("delete")
def delete_note(ctx: Context, name: Autocomplete[str]):
    "Delete an existing note"
    user = database[ctx.author]
    user_notes = user.setdefault("notes", {})
    if name not in user_notes:
        return Message(f"Note {name} not found", ephemeral=True)
    else:
        user_notes.pop(name)
        return Message(f"Note {name} deleted", ephemeral=True)


@get_note.autocomplete()
@set_note.autocomplete()
@note_modal.autocomplete()
@update_note.autocomplete()
@delete_note.autocomplete()
def note_name_autocomplete_handler(ctx, name: Option = None, **_):
    if name is None or not name.focused:
        return []
    user = database[ctx.author]
    user_notes = user.setdefault("notes", {})
    options = []
    for key, description in user_notes.items():
        if key.startswith(name.value):
            display = f"{key}: {description}"
            if len(display) > 100:
                display = display[:97] + '...'
            options.append(Choice(name=display, value=key))
            # It will visually fill in the command with the `name` if you click it, 
            # but it will send with the correct `value` even then
    options.sort(key=lambda option: option.name)
    return options[:25]
