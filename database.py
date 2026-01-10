# database.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import DB_URL

engine = create_async_engine(DB_URL)

async def add_expense(group_id, payer, amount, desc, excluded=""):
    async with engine.begin() as conn:
        query = text("""
            INSERT INTO expenses (group_id, payer_name, amount, description, excluded_users)
            VALUES (:group_id, :name, :amount, :desc, :excl)
        """)
        await conn.execute(query, {
            "group_id": group_id, "name": payer, 
            "amount": amount, "desc": desc, "excl": excluded
        })

async def get_expenses(group_id):
    async with engine.connect() as conn:
        query = text("SELECT payer_name, amount, excluded_users FROM expenses WHERE group_id = :group_id")
        result = await conn.execute(query, {"group_id": group_id})
        return result.all()

async def clear_group_data(group_id):
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM expenses WHERE group_id = :group_id"), {"group_id": group_id})

# ... (твои старые импорты)

# ... старые импорты ...

async def set_language(group_id, lang_code):
    async with engine.begin() as conn:
        # Если настройки нет - создаем, если есть - обновляем (Upsert)
        query = text("""
            INSERT INTO group_settings (group_id, lang_code)
            VALUES (:group_id, :lang)
            ON CONFLICT (group_id) DO UPDATE SET lang_code = :lang
        """)
        await conn.execute(query, {"group_id": group_id, "lang": lang_code})

async def get_language(group_id):
    async with engine.connect() as conn:
        query = text("SELECT lang_code FROM group_settings WHERE group_id = :group_id")
        result = await conn.execute(query, {"group_id": group_id})
        row = result.fetchone()
        # Если в базе нет записи, по умолчанию возвращаем 'ru'
        return row[0] if row else 'ru'

async def add_participant(group_id, user_name):
    async with engine.begin() as conn:
        # ON CONFLICT DO NOTHING означает: если он уже есть, ошибку не выдаем, просто пропускаем
        query = text("""
            INSERT INTO participants (group_id, user_name)
            VALUES (:group_id, :name)
            ON CONFLICT (group_id, user_name) DO NOTHING
        """)
        await conn.execute(query, {"group_id": group_id, "name": user_name})

async def get_participants(group_id):
    async with engine.connect() as conn:
        query = text("SELECT user_name FROM participants WHERE group_id = :group_id")
        result = await conn.execute(query, {"group_id": group_id})
        # Превращаем ответ базы в простой список строк ['Omaz', 'Ansar']
        return [row[0] for row in result.all()]

# --- ВАЖНО: Обнови функцию очистки, чтобы удалялись и участники тоже ---
async def clear_group_data(group_id):
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM expenses WHERE group_id = :group_id"), {"group_id": group_id})
        await conn.execute(text("DELETE FROM participants WHERE group_id = :group_id"), {"group_id": group_id})