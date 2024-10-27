from dataclasses import dataclass


@dataclass
class Game:
    id: str  # internal identifier
    modio_id: int  # ID for mod.io
    full_name: str  # Display name for the game
    data_types: list[str]  # List of the tag types in the game
    is_public: bool  # Restrict who can get that game's data with the bot commands


@dataclass
class GameRecord:
    game_id: str  # which game it is from
    mod: str  # which mod it is from
    tag: str  # tag type
    id: str  # identifier
    path: str  # relative path to the file it's defined in, starting from the Game's full name
    is_public: bool  # Restrict who can get that record with the bot commands
    xml: str  # might have to think some more about that one later
