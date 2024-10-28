import asyncio
from typing import Sequence
from pathlib import Path
from xml.etree import ElementTree as ET

from fishybot.database import GameRecord, create_session

def filter_records(records: Sequence[GameRecord], xpath: str) -> list[GameRecord]:
    results = []
    for record in records:
        root = ET.fromstring(record.xml)
        if root.find(path=xpath) is not None:
            results.append(record)
    return results


async def test():
    from sqlalchemy import select
    statement = (
        select(GameRecord)
        .where(GameRecord.game_id == "aground")
        .where(GameRecord.tag == "item")
    )

    DB_FILE = Path.cwd() / "fancyfish.sqlite"
    # XPATH = R"""[@id="wyrm"]"""
    XPATH = R"""[@element="fire"]"""

    async with create_session(str(DB_FILE.resolve())) as session_pool:
        async with session_pool() as session:
            records = await session.scalars(statement)
    
    results = filter_records(records.fetchall(), XPATH)
    print(*(result.id for result in results), sep='\n')
    # print(*(result.xml for result in results), sep='\n')


if __name__ == '__main__':
    asyncio.run(test())
