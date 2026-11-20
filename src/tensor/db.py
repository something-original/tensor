import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .sql_commands import (
    create_departments_table,
    create_empolyees_table,
    create_offices_table,
    get_tables_count
)

engine = None
async_session = None


async def get_session():
    async with async_session() as session:
        yield session


async def check_init_database(db_url: str):
    global engine
    global async_session

    if engine is None:
        engine = create_async_engine(db_url)
        async_session = async_sessionmaker(engine)

    async with engine.connect() as connection:
        await connection.execute(sa.text(create_departments_table))
        await connection.execute(sa.text(create_empolyees_table))
        await connection.execute(sa.text(create_offices_table))
        await connection.commit()

    async for session in get_session():
        tables_count = (await session.execute(sa.text(get_tables_count))).all()
        print(tables_count)
