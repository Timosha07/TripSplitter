import os
from dotenv import load_dotenv
load_dotenv()

def database_url():
    url = os.getenv("DATABASE_URL", "")
    if not url.startswith(("postgresql://", "postgres://")):
        raise RuntimeError("Set DATABASE_URL to a PostgreSQL connection URL")
    return url

def bot_token():
    token = os.getenv("BOT_TOKEN", "")
    if not token:
        raise RuntimeError("Set BOT_TOKEN in .env")
    return token
