import logging

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from .parser import parse_fill_tables
from .sql_commands import create_empolyees_table, get_employees_count, select_people_by_id

engine = None
async_session = None

logger = logging.getLogger(__name__)


async def get_session():
    async with async_session() as session:
        yield session


async def check_init_database(db_url: str, file_path: str) -> None:
    global engine
    global async_session

    if engine is None:
        engine = create_async_engine(db_url)
        async_session = async_sessionmaker(engine)

    logger.info("Creating table if not exists")
    async with engine.connect() as connection:
        await connection.execute(sa.text(create_empolyees_table))
        await connection.commit()

    async for session in get_session():
        employees_count = (await session.execute(sa.text(get_employees_count))).scalar()
        if employees_count != 0:
            logger.info("Table is not empty, skipping initialization")
            return
        
        logger.info("Initializing table")
        await parse_fill_tables(session, file_path)


async def get_people_in_office_by_id(session: AsyncSession, employee_id: int) -> list[str]:
    res = (
        await session.execute(
            sa.text(select_people_by_id), {"employee_id": employee_id}
        )
    ).scalars().all() or []
    return res
