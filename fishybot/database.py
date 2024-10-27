import contextlib
import typing

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Game(Base):
    __tablename__ = "game"
    pk: Mapped[int] = mapped_column(primary_key=True) 
    id: Mapped[str] # internal identifier
    modio_id: Mapped[int]  # ID for mod.io
    full_name: Mapped[str]  # Display name for the game
    # data_types: Mapped[list[str]]  # List of the tag types in the game
    data_types: Mapped[str]  # comma separated string representing a list of the tag types in the game
    is_public: Mapped[bool]  # Restrict who can get that game's data with the bot commands
    records: Mapped[list["GameRecord"]] = relationship("GameRecord", back_populates="game")


class GameRecord(Base):
    __tablename__ = "game_record"
    pk: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("game.id"))  # which game it is from
    game: Mapped[Game] = relationship("Game", back_populates="records")
    mod: Mapped[str]  # which mod it is from
    tag: Mapped[str]  # tag type
    id: Mapped[str]  # identifier
    path: Mapped[str]  # relative path to the file it's defined in, starting from the Game's full name
    is_public: Mapped[bool]  # Restrict who can get that record with the bot commands
    xml: Mapped[str]  # might have to think some more about that one later

# async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
#     async with async_session() as session:
#         async with session.begin():
#             session.add_all(
#                 [
#                     A(bs=[B(data="b1"), B(data="b2")], data="a1"),
#                     A(bs=[], data="a2"),
#                     A(bs=[B(data="b3"), B(data="b4")], data="a3"),
#                 ]
#             )


# async def select_and_update_objects(
#     async_session: async_sessionmaker[AsyncSession],
# ) -> None:
#     async with async_session() as session:
#         stmt = select(A).order_by(A.id).options(selectinload(A.bs))
#         result = await session.execute(stmt)
#         for a in result.scalars():
#             print(a, a.data)
#             print(f"created at: {a.create_date}")
#             for b in a.bs:
#                 print(b, b.data)
#         result = await session.execute(select(A).order_by(A.id).limit(1))
#         a1 = result.scalars().one()
#         a1.data = "new data"
#         await session.commit()
#         # access attribute subsequent to commit; this is what
#         # expire_on_commit=False allows
#         print(a1.data)
#         # alternatively, AsyncAttrs may be used to access any attribute
#         # as an awaitable (new in 2.0.13)
#         for b1 in await a1.awaitable_attrs.bs:
#             print(b1, b1.data)


# async def async_main() -> None:
#     engine = create_async_engine("sqlite+aiosqlite://", echo=True)
#     # async_sessionmaker: a factory for new AsyncSession objects.
#     # expire_on_commit - don't expire objects after transaction commit
#     async_session = async_sessionmaker(engine, expire_on_commit=False)
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     await insert_objects(async_session)
#     await select_and_update_objects(async_session)
#     # for AsyncEngine created in function scope, close and
#     # clean-up pooled connections
#     await engine.dispose()

@contextlib.asynccontextmanager
async def create_session(path: str) -> typing.AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    engine = create_async_engine(f"sqlite+aiosqlite:///{path}")
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield async_session
    finally:
        await engine.dispose()


# asyncio.run(async_main())


if __name__ == "__main__":
    import asyncio
    from sqlalchemy import select
    async def test():
        async with create_session("fancyfish.sqlite") as pool:
            async with pool() as session:
                results = await session.scalars(
                    select(GameRecord)
                    .where(GameRecord.game_id == "aground")
                    .where(GameRecord.tag == "item")
                    .where(GameRecord.id == "wyrm")
                )
                data = results.first()
                print(data)
                assert data is not None
                print(data.xml)
                print(vars(data) | {'xml': ...})

    asyncio.run(test())
