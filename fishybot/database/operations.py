import sqlite3

from common.exceptions import GameNotFoundError, TagNotFoundError, RecordNotFoundError 
from database.sqlite_model import Game, GameRecord


def get_possible_games(game_prefix: str, include_hidden: bool) -> list[Game]:
    """Returns all games that match the given `game_prefix`"""
    results = []
    query = """SELECT id, modio_id, full_name, data_types, is_public
            FROM game WHERE id LIKE ?"""
    if not include_hidden:
        query += " AND is_public = 1"
    with sqlite3.connect("fancyfish.sqlite") as connection:
        for game in connection.execute(
            query,
            (f"{game_prefix}%",)
        ).fetchall():
            game = Game(*game)
            game.data_types = game.data_types.split(", ")
            results.append(game)
    return results


def get_possible_tags(game: str, tag_prefix: str, include_hidden: bool) -> list[str]:
    """Returns all tags for game `game` that match the given `tag_prefix`."""
    results = []
    query = "SELECT id, data_types FROM game WHERE id = ?"
    if not include_hidden:
        query += " AND is_public = 1"
    with sqlite3.connect("fancyfish.sqlite") as connection:
        game = connection.execute(query, (game,)).fetchone()
        if game is None:
            raise GameNotFoundError()
        tags = game[1].split(", ")
        for tag in tags:
            if tag.startswith(tag_prefix):
                results.append(tag)
    return results


def get_exact_record(game: str, tag: str, record_id: str, include_xml: bool, include_hidden: bool) -> GameRecord:
    """Return a single `tag` GameRecord for `game` whose `id` exactly matches `id_part`.
    Raises RecordNotFoundError if there isn't one that perfectly matches it."""
    if include_xml:
        query = """SELECT game_id, mod, tag, id, path, is_public, xml
        FROM game_record WHERE game_id = ? AND tag = ? AND id = ?"""
    else:
        query = """SELECT game_id, mod, tag, id, path, is_public
        FROM game_record WHERE game_id = ? AND tag = ? AND id = ?"""
    if not include_hidden:
        query += " AND is_public=1"
    with sqlite3.connect("fancyfish.sqlite") as connection:
        row = connection.execute(query, (game, tag, record_id)).fetchone()
        if row is None:
            raise RecordNotFoundError()
        return GameRecord(*row)


def get_matching_records(game: str, tag: str, id_part: str, include_xml: bool, include_hidden: bool, limit: int = 25) -> list[GameRecord]:
    """Returns all `tag` Records for `game` whose `id` include `id_part`."""
    results = []
    if include_xml:
        query = """SELECT game_id, mod, tag, id, path, is_public, xml
        FROM game_record WHERE game_id = ? AND tag = ? AND id LIKE ?"""
    else:
        query = """SELECT game_id, mod, tag, id, path, is_public
        FROM game_record WHERE game_id = ? AND tag = ? AND id LIKE ?"""
    if not include_hidden:
        query += " AND is_public=1"
    if limit:
        assert isinstance(limit, int)
        query += f" LIMIT {limit}"
    with sqlite3.connect("fancyfish.sqlite") as connection:
        for row in connection.execute(query, (game, tag, f'%{id_part}%')).fetchall():
            record = GameRecord(*row)
            results.append(record)
    return results
