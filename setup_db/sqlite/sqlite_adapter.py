import sqlite3

from model import Game, GameRecord
from gather_games import gather

import dataclasses


def insert_data(games: dict[str, Game], games_data: dict[str, GameRecord]):
    database = sqlite3.connect("fancyfish.sqlite")

    cur = database.cursor()

    for game in games.values():
        game.data_types = ", ".join(game.data_types)
    try:
        cur.execute("DROP TABLE IF EXISTS game")
        cur.execute("DROP TABLE IF EXISTS game_record")

        cur.execute("CREATE TABLE game (id, modio_id, full_name, data_types, is_public)")
        cur.execute("CREATE TABLE game_record (game_id, mod, tag, id, path, is_public, xml)")

        games = (dataclasses.astuple(game) for game in games.values())
        games_data = (dataclasses.astuple(record) for record in games_data.values())

        cur.executemany("INSERT INTO game VALUES (?, ?, ?, ?, ?)", games)
        cur.executemany("INSERT INTO game_record VALUES (?, ?, ?, ?, ?, ?, ?)", games_data)

        database.commit()
    finally:
        cur.close()
        database.close()


def main():
    games, data = gather()
    insert_data(games, data)


if __name__ == "__main__":
    main()
