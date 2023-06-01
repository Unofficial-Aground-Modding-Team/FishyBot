class BotError(Exception):
    "Base class used for our custom exceptions"  # not that we need it


class GameNotFoundError(BotError):
    "No games match the given filters"


class TagNotFoundError(BotError):
    "The given tag is not valid"


class RecordNotFoundError(BotError):
    "There were no matches for that specific record"

class InvalidQueryError(BotError):
    "There was an error trying to execute an user supplied Query"

