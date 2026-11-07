"""Windows local PostgreSQL setup and bot launcher. Secrets stay in .env."""
import argparse
import asyncio
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
from urllib.parse import urlparse

import asyncpg
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent
LOCAL = ROOT / '.local'
DATA = LOCAL / 'postgres'
PORT = 55440
USER = 'tripsplitter'
DB = 'tripsplitter_v2'

def postgres_bin():
    candidates = list((Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'PostgreSQL').glob('*/bin'))
    candidates.sort(key=lambda p: int(p.parent.name) if p.parent.name.isdigit() else 0, reverse=True)
    for path in candidates:
        if (path / 'pg_ctl.exe').is_file():
            return path
    raise RuntimeError('PostgreSQL not found in Program Files/PostgreSQL.')

def execute(binary, *args, check=True):
    return subprocess.run([str(postgres_bin() / binary), *map(str, args)],
                          cwd=ROOT, check=check, creationflags=subprocess.CREATE_NO_WINDOW)

def settings():
    env_file = ROOT / '.env'
    if not env_file.exists():
        password = secrets.token_urlsafe(32)
        # Exclusive creation prevents replacing credentials written by another process.
        with env_file.open('x', encoding='utf-8') as out:
            out.write(f'BOT_TOKEN=\nDATABASE_URL=postgresql://{USER}:{password}@127.0.0.1:{PORT}/{DB}\n')
    values = dotenv_values(env_file)
    url = urlparse(values.get('DATABASE_URL', ''))
    if (url.scheme != 'postgresql' or url.hostname != '127.0.0.1' or url.port != PORT
            or url.username != USER or url.path != '/' + DB or not url.password):
        raise RuntimeError('Existing .env uses another database. Configure it manually; local setup will not overwrite it.')
    return values, url

def start_database():
    LOCAL.mkdir(exist_ok=True)
    values, url = settings()
    if not (DATA / 'PG_VERSION').exists():
        fd, filename = tempfile.mkstemp(prefix='init-', dir=LOCAL)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as out:
                out.write(url.password + '\n')
            execute('initdb.exe', '-D', DATA, '-U', USER, '--auth-host=scram-sha-256',
                    '--auth-local=scram-sha-256', '--encoding=UTF8', '--no-locale', '--pwfile', filename)
        finally:
            Path(filename).unlink(missing_ok=True)
    status = execute('pg_ctl.exe', '-D', DATA, 'status', check=False)
    if status.returncode != 0:
        execute('pg_ctl.exe', '-D', DATA, '-l', LOCAL / 'postgres.log',
                '-o', f'-h 127.0.0.1 -p {PORT}', '-w', 'start')
    return values, url

async def prepare(values, url):
    conn = await asyncpg.connect(host='127.0.0.1', port=PORT, user=USER,
                                 password=url.password, database='postgres', timeout=10)
    try:
        if not await conn.fetchval('SELECT 1 FROM pg_database WHERE datname=$1', DB):
            await conn.execute(f'CREATE DATABASE {DB}')
    finally:
        await conn.close()
    os.environ['DATABASE_URL'] = values['DATABASE_URL']
    from migrate import migrate
    await migrate()
    from database import Store
    store = Store(values['DATABASE_URL'])
    try:
        await store.open()
        await store.read(0)
    finally:
        await store.close()
    print(f'Database ready: {DB}, 127.0.0.1:{PORT}. Credentials are in .env.')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['setup', 'run', 'stop', 'status'], default='setup', nargs='?')
    action = parser.parse_args().action
    if action in ('stop', 'status'):
        if not (DATA / 'PG_VERSION').exists():
            print('Local database has not been created.')
            return
        args = ['-D', DATA]
        execute('pg_ctl.exe', *args, *(['-m', 'fast', '-w', 'stop'] if action == 'stop' else ['status']), check=False)
        return
    values, url = start_database()
    asyncio.run(prepare(values, url))
    if action == 'run':
        token = values.get('BOT_TOKEN', '')
        if not token:
            print('Add BOT_TOKEN to .env, save it, then double-click start.cmd again.')
            return
        from aiogram.utils.token import validate_token
        validate_token(token)
        os.environ['BOT_TOKEN'] = token
        from bot import main as run_bot
        asyncio.run(run_bot())

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f'Setup failed: {exc}')
        raise SystemExit(1) from None
