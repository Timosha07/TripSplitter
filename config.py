import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Достаем токен
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Достаем пароль от базы и собираем ссылку
DB_PASS = os.getenv("DB_PASS")
DB_URL = f"postgresql+asyncpg://postgres:{DB_PASS}@localhost:5432/trip_splitter_db"