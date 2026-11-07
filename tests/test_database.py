import asyncio
import os
import uuid
import pytest
from database import Store
import domain as d

@pytest.mark.skipif(not os.getenv('TEST_DATABASE_URL'), reason='Requires disposable PostgreSQL TEST_DATABASE_URL')
def test_postgres_migration_transactions_and_concurrency(monkeypatch):
    async def run():
        from migrate import migrate
        monkeypatch.setenv('DATABASE_URL', os.environ['TEST_DATABASE_URL'])
        await migrate()
        await migrate()
        store = Store(os.environ['TEST_DATABASE_URL'])
        await store.open()
        chat = -(uuid.uuid4().int % 10**15)
        try:
            async with store.edit(chat) as s:
                d.register(s, 1, 'Alice')
                d.register(s, 2, 'Bob')
            async def insert(i):
                async with store.edit(chat) as s:
                    d.add(s, str(i), 1, 101, '1.01', 'KZT', '1', 'taxi', [])
            await asyncio.gather(*(insert(i) for i in range(20)))
            state = await store.read(chat)
            assert len(state['expenses']) == 20
            assert sum(d.balances(state).values()) == 0
            with pytest.raises(RuntimeError):
                async with store.edit(chat) as s:
                    s['language'] = 'en'
                    raise RuntimeError('rollback')
            assert (await store.read(chat))['language'] == 'ru'
            with pytest.raises(d.Invalid):
                await insert(1)
            assert len((await store.read(chat))['expenses']) == 20
        finally:
            async with store.pool.acquire() as conn:
                await conn.execute('DELETE FROM ts_ledgers WHERE chat_id=$1', chat)
            await store.close()
    asyncio.run(run())
