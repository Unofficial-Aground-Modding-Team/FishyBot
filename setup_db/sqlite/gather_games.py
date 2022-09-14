import re
from typing import Generator
from lxml import etree
from pathlib import Path

from model import Game, GameRecord

PARSER = etree.XMLParser(recover=True)


def get_paths_to_search(prefix: Path, games: list[Game]) -> Generator[tuple[Game, str, Path], None, None]:
    """
    Yields the (Game, mod_name, mod.xml file Path) tuples for each mod found for each game

    Parameters
    ----------
    prefix : Path
        The folder in which the Games are stored
    games : list[Game]
        List of Fancy Fish Games's games to be searched.
    """
    for game in games:
        game_path = prefix / game.full_name / "data"
        yield (
            game,
            "core",
            game_path / 'core' / 'mod.xml',
        )
        mods_folder = game_path / 'mods'
        if mods_folder.is_dir():
            for mod_path in mods_folder.iterdir():
                if (mod_path / 'mod.xml').is_file():
                    yield (
                        game,
                        mod_path.stem,
                        mod_path / 'mod.xml',
                    )


def should_ignore_node(element: etree._Element):
    if element.tag == "tilesheet":
        if re.match(r"\w+\.\d+", element.get("id")):
            return True


def process_lang(game: Game, mod: str, root: etree._Element):
    # TODO SAVE IT IN SOME WAY
    # print(f"Process lang called for {game.full_name} {mod} {root.get('id')}")
    pass


def check_sub_mod(mod: str, include_target: Path):
    if "full\\colosseum" in str(include_target):
        return "colosseum"
    elif "full\\hybrid_path" in str(include_target):
        return "hybrid_path"
    else:
        return mod


def crawl_file(
    game: Game,
    mod: str,
    prefix_path: Path,
    filepath: Path,
    include_root: bool = False,
) -> Generator[GameRecord, None, None]:
    """Craws a file and yields all GameRecords found.
    Recursively follows <include>s.
    """
    tree: etree._ElementTree = etree.parse(filepath, parser=PARSER)
    root: etree._Element = tree.getroot()

    def process_element(element):
        if should_ignore_node(element):
            return
        id_ = element.get("id")
        tag = element.tag
        if tag == "include":
            include_target: Path = filepath.parent / element.get("id")
            if include_target.is_file():
                yield from crawl_file(
                    game,
                    check_sub_mod(mod, include_target),
                    prefix_path,
                    include_target,
                    element.get("includeRoot") == "true",
                )
            else:
                # Known to happen to: Aground\data\mods\full\music\music.xml
                print(f"[WARNING] Skipping path {include_target}")
        elif tag == "lang":
            process_lang(game, mod, element)
        elif id_ is not None:
            yield GameRecord(
                game.id,
                mod,
                tag,
                id_,
                str(filepath.relative_to(prefix_path)).replace("\\", "/"),
                game.is_public and mod == "core",
                etree.tostring(element, pretty_print=True).decode(),
            )

    if include_root:
        yield from process_element(root)
    elif filepath.name == "mod.xml":
        for child in root.find("init"):
            yield from process_element(child)
    else:
        for child in root:
            yield from process_element(child)


def gather() -> tuple[dict[str, Game], dict[str, GameRecord]]:
    PREFIX = Path(r"C:\Program Files (x86)\Steam\steamapps\common" + '\\')


    games = {
        "aground": Game("aground", 34, "Aground", None, True),
        "stardander_revenant": Game("stardander_revenant", -1, "Stardander Revenant", None, True),
        "aground_zero": Game("aground_zero", -1, "Aground Zero Playtest", None, False),
        "stardander": Game("stardander", -1, "Stardander Playtest", None, False),
    }
    _games_tags: dict[str, set[str]] = {}

    paths = get_paths_to_search(PREFIX, games.values())
    data: dict[str, GameRecord] = {}

    for (game, mod, full_path) in paths:
        records = crawl_file(game, mod, PREFIX, full_path)

        for record in records:
            key_path = (
                record
                .path
                .casefold()
                .replace(' ', '_')
                .removesuffix(".xml")
                .split('/')
            )
            if key_path[2] == "mods":
                del key_path[2]
            if key_path[1] == "data":
                del key_path[1]

            key_path = '_'.join(key_path)
            key = """{1}_{0.tag}_{0.id}""".format(record, key_path)

            if key in data:
                # Known to happen to: aground_core_items_item_chest
                # also sometimes to some mods
                print(f"[WARNING] Ignoring Duplicated key {key}")
                # data[key].xml += record.xml
            else:
                data[key] = record
            
            _games_tags.setdefault(record.game_id, set()).add(record.tag)

    for game_id, game_tags in _games_tags.items():
        games[game_id].data_types = list(game_tags)

    return games, data


if __name__ == "__main__":
    games, records = gather()

    print()
    import random
    pick = random.sample(list(records.items()), k=10)
    print(*pick, sep='\n\n\n')