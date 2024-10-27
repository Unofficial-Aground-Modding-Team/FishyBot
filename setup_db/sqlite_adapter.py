import sqlite3

from model import Game, GameRecord
from gather_games import gather

import dataclasses


def insert_data(games: dict[str, Game], games_data: dict[str, GameRecord]):
    database = sqlite3.connect("fancyfish.sqlite")

    cur = database.cursor()

    for game in games.values():
        game.data_types = ", ".join(game.data_types) # type: ignore
    try:
        cur.execute("DROP TABLE IF EXISTS game")
        cur.execute("DROP TABLE IF EXISTS game_record")

        cur.execute("CREATE TABLE game (pk INTEGER PRIMARY KEY AUTOINCREMENT, id STRING, modio_id INTEGER, full_name STRING, data_types STRING, is_public BOOLEAN)")
        cur.execute("CREATE TABLE game_record (pk INTEGER PRIMARY KEY AUTOINCREMENT, game_id STRING, mod STRING, tag STRING, id STRING, path STRING, is_public BOOLEAN, xml STRING)")
        
        games_tuples = (dataclasses.astuple(game) for game in games.values())
        games_data_tuples = (dataclasses.astuple(record) for record in games_data.values())

        cur.executemany("INSERT INTO game (id, modio_id, full_name, data_types, is_public) VALUES (?, ?, ?, ?, ?)", games_tuples)
        cur.executemany("INSERT INTO game_record (game_id, mod, tag, id, path, is_public, xml) VALUES (?, ?, ?, ?, ?, ?, ?)", games_data_tuples)

        database.commit()
    finally:
        cur.close()
        database.close()


def main():
    games, data = gather()
    insert_data(games, data)


if __name__ == "__main__":
    main()
