"""Versioned PostgreSQL ledger; one row lock serializes each chat's writes."""
import json
from contextlib import asynccontextmanager
import asyncpg
from domain import empty

class Store:
    def __init__(self, url):
        self.url = url
        self.pool = None

    async def open(self):
        self.pool = await asyncpg.create_pool(self.url, min_size=1, max_size=5, command_timeout=15)
        async with self.pool.acquire() as conn:
            version = await conn.fetchval("SELECT version FROM ts_schema WHERE id = 1")
            if version != 1:
                raise RuntimeError("Unsupported schema: run python migrate.py")

    async def close(self):
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def edit(self, chat_id):
        async with self.pool.acquire() as conn, conn.transaction():
            await conn.execute("INSERT INTO ts_ledgers (chat_id, data) VALUES ($1, $2::jsonb) ON CONFLICT DO NOTHING", chat_id, json.dumps(empty()))
            raw = await conn.fetchval("SELECT data FROM ts_ledgers WHERE chat_id=$1 FOR UPDATE", chat_id)
            state = json.loads(raw)
            yield state
            await conn.execute("UPDATE ts_ledgers SET data=$2::jsonb WHERE chat_id=$1", chat_id, json.dumps(state))

    async def read(self, chat_id):
        async with self.pool.acquire() as conn:
            raw = await conn.fetchval("SELECT data FROM ts_ledgers WHERE chat_id=$1", chat_id)
            return json.loads(raw) if raw else empty()
