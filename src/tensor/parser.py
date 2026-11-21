import json
import logging
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from .sql_commands import insert_employees_data


logger = logging.getLogger(__name__)

async def parse_fill_tables(session: AsyncSession, file_path: str) -> None:
    with open(file_path, "r", encoding="utf-8-sig") as f:
        people_data = json.loads(f.read())

    logger.info("File read")

    insert_values_clause_list = []
    for row in people_data:
        row_items = []
        for item in row.values():
            if not isinstance(item, str | None):
                row_items.append(str(item))
            if item is None:
                row_items.append('NULL')
            if isinstance(item, str):
                row_items.append(f"'{item}'")

        insert_values_clause_list.append(f"({', '.join(row_items)})")

    insert_values_clause = ",\n".join(insert_values_clause_list)

    await session.execute(sa.text(insert_employees_data.format(values_clause=insert_values_clause)))
    await session.commit()

    logger.info("Vaules inserted")
