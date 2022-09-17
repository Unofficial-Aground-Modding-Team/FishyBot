import sqlite3

from model import Game, GameRecord

def get_games(cursor):
    cursor.execute("SELECT * FROM game LIMIT 10")
    results = [Game(*result) for result in cursor.fetchall()]
    for result in results:
        result.data_types = sorted(result.data_types.split(", "))
    return results


def get_data(cursor):
    cursor.execute("SELECT * FROM game_record LIMIT 10")
    return [GameRecord(*result) for result in cursor.fetchall()]



def main():
    con = sqlite3.connect("fancyfish.sqlite")
    cur = con.cursor()
    try:
        print("---GAMES---")
        print(*get_games(cur), sep='\n\n')
        print("\n---RECORDS---\n")
        print(*get_data(cur), sep='\n\n')
    finally:
        cur.close()
        con.close()


if __name__ == "__main__":
    main()