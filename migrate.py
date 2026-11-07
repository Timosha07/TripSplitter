"""Apply additive migrations; refuse unreviewed legacy data migration."""
import asyncio
import asyncpg
from config import database_url

async def migrate():
    conn = await asyncpg.connect(database_url())
    try:
        async with conn.transaction():
            await conn.execute("SELECT pg_advisory_xact_lock(71432001)")
            legacy = await conn.fetchval("SELECT to_regclass('public.expenses')")
            if legacy:
                raise RuntimeError("Legacy expenses table found. See MIGRATION.md; use a separate database for v2.")
            await conn.execute("CREATE TABLE IF NOT EXISTS ts_schema (id INTEGER PRIMARY KEY CHECK (id=1), version INTEGER NOT NULL)")
            version = await conn.fetchval("SELECT version FROM ts_schema WHERE id=1")
            if version not in (None, 1):
                raise RuntimeError("Unsupported schema version")
            await conn.execute("CREATE TABLE IF NOT EXISTS ts_ledgers (chat_id BIGINT PRIMARY KEY, data JSONB NOT NULL CHECK (jsonb_typeof(data)='object'))")
            await conn.execute("INSERT INTO ts_schema VALUES (1,1) ON CONFLICT DO NOTHING")
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(migrate())
