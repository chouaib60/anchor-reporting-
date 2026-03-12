import asyncio
import asyncpg
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_settings
from models.user import CREATE_USERS_TABLE
from models.template import CREATE_TEMPLATES_TABLE, CREATE_TEMPLATE_VERSIONS_TABLE

settings = get_settings()

async def main():
    conn = await asyncpg.connect(settings.database_url.replace("+asyncpg", ""))

    await conn.execute(CREATE_USERS_TABLE)
    print("Table users creee")

    await conn.execute(CREATE_TEMPLATES_TABLE)
    print("Table templates creee")

    await conn.execute(CREATE_TEMPLATE_VERSIONS_TABLE)
    print("Table template_versions creee")

    tables = await conn.fetch("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    print("Tables presentes :", [r["tablename"] for r in tables])

    await conn.close()

asyncio.run(main())