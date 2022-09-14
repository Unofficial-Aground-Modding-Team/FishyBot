import sqlite3
from xml.etree import ElementTree

from database.sqlite_model import GameRecord
from common.exceptions import InvalidQueryError
# from sqlite_model import GameRecord
# class InvalidQueryError():
#     pass


def get_matching_records(game: str, tag: str, xpath: str, include_hidden: bool, limit: int = 25) -> list[GameRecord]:
    """Returns all `tag` Records for `game` whose `id` include `id_part`."""
    results = []
    query = """SELECT game_id, mod, tag, id, path, is_public, xml
        FROM game_record WHERE game_id = ? AND tag = ?"""
    if not include_hidden:
        query += " AND is_public=1"
    with sqlite3.connect("fancyfish.sqlite") as connection:
        for row in connection.execute(query, (game, tag)).fetchall():
            record = GameRecord(*row)
            try:
                if ElementTree.fromstring(record.xml).findall(xpath):
                    results.append(record)
                    if len(results) >= limit:
                        break
            except Exception:
                # breakpoint()
                raise InvalidQueryError(xpath, record)
    return results

if __name__ == "__main__":
    # test = get_matching_records("aground", "item", "[@type='food']", False)
    # test = get_matching_records("aground", "item", "stat[@max]", False)
    # test = get_matching_records("aground", "item", "./action/tile", False)
    test = get_matching_records("aground", "recipe", "[@type='magic_forge']", False)
    print(*test, sep='\n\n')
