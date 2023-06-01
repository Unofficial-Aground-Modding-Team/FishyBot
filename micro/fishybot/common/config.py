import pathlib
BOT_COLOR = 0x3fc9e7

sqlite_database_path = pathlib.Path(__file__).parent.parent / 'fancyfish.sqlite'
assert sqlite_database_path.is_file(), "Local SQLite database not found"