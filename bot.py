import asyncio
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from texts import MESSAGES 
from config import BOT_TOKEN
import database as db
import logic
import currency

# 1. Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

# Функция, которая выбирает единое имя для пользователя (исправляет баг с дублями)
def get_name(user: types.User):
    if user.username:
        return f"@{user.username}"
    return user.first_name

async def get_msg(chat_id, key):
    lang = await db.get_language(chat_id)
    return MESSAGES.get(lang, MESSAGES['ru']).get(key, key)

# --- ОБРАБОТЧИКИ КОМАНД ---

@dp.message(Command("start"))
async def start(message: types.Message):
    text = await get_msg(message.chat.id, "welcome")
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    text = await get_msg(message.chat.id, "welcome")
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("paid"))
async def handle_paid(message: types.Message):
    text = message.text
    chat_id = message.chat.id
    
    # 1. Ищем сумму и валюту
    match = re.search(r"(\d+(?:\.\d+)?)\s+([a-zA-Z]{3})", text)
    amount = 0.0
    currency_code = "KZT"
    
    if match:
        amount = float(match.group(1))
        currency_code = match.group(2).upper()
    else:
        match_simple = re.search(r"(\d+(?:\.\d+)?)", text)
        if not match_simple:
            # Берем текст ошибки из словаря
            err_msg = await get_msg(chat_id, "err_no_sum")
            return await message.answer(err_msg)
        amount = float(match_simple.group(1))

    # 2. Конвертация
    rate = 1.0
    final_amount_kzt = amount
    
    if currency_code != "KZT":
        # Сообщение "Ищу курс..." можно оставить универсальным или тоже добавить в словарь
        # Для простоты пока оставим или сделаем эмодзи
        await message.answer(f"🔎 {currency_code} ➡️ KZT...")
        rate = currency.get_exchange_rate(currency_code)
        
        if rate is None:
            err_rate = await get_msg(chat_id, "err_no_rate")
            return await message.answer(err_rate.format(currency=currency_code))
        
        final_amount_kzt = amount * rate

    # 3. Ищем исключения
    excluded = []
    if "except" in text.lower():
        for entity in message.entities or []:
            if entity.type == "mention":
                username = text[entity.offset:entity.offset + entity.length]
                excluded.append(username)
    
    # 4. Описание и Имя
    description = re.sub(r"/paid\s*\d+(?:\.\d+)?(\s+[a-zA-Z]{3})?", "", text)
    description = description.split("except")[0].strip() or "---"
    payer_name = get_name(message.from_user)

    # 5. Сохраняем в базу
    await db.add_expense(
        group_id=chat_id,
        payer=payer_name,
        amount=final_amount_kzt,
        desc=f"{description} (orig: {amount} {currency_code})",
        excluded=",".join(excluded)
    )
    
    # 6. Формируем ответ на нужном языке!
    pretty_kzt = int(final_amount_kzt)
    
    # Берем шаблоны
    tmpl_header = await get_msg(chat_id, "paid_header")
    tmpl_cur = await get_msg(chat_id, "paid_cur")
    tmpl_desc = await get_msg(chat_id, "paid_desc")
    
    # Собираем ответ
    response_text = tmpl_header.format(name=payer_name, amount=pretty_kzt)
    
    if currency_code != "KZT":
        response_text += tmpl_cur.format(original=f"{amount} {currency_code}", rate=rate)
        
    response_text += tmpl_desc.format(desc=description)
    
    await message.answer(response_text, parse_mode="HTML")

@dp.message(Command("join"))
async def cmd_join(message: types.Message):
    user_name = get_name(message.from_user)
    await db.add_participant(message.chat.id, user_name)
    
    # Берем текст из словаря и вставляем имя
    tmpl = await get_msg(message.chat.id, "join_msg")
    await message.answer(tmpl.format(name=user_name), parse_mode="HTML")

@dp.message(Command("lang"))
async def cmd_lang(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang_kz")],
        [InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en")]
    ])
    # Берем дефолтный русский текст для выбора, чтобы не усложнять
    await message.answer(MESSAGES['ru']['choose_lang'], reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith('lang_'))
async def process_lang_callback(callback: CallbackQuery):
    lang_code = callback.data.split("_")[1]
    await db.set_language(callback.message.chat.id, lang_code)
    new_text = MESSAGES[lang_code]['lang_set']
    await callback.answer()
    await callback.message.answer(new_text)

@dp.message(Command("stop"))
async def calculate_final(message: types.Message):
    chat_id = message.chat.id
    expenses = await db.get_expenses(chat_id)
    participants = await db.get_participants(chat_id)
    
    if not expenses and not participants:
        text = await get_msg(chat_id, "group_empty")
        return await message.answer(text)

    wait_text = await get_msg(chat_id, "calc_start")
    await message.answer(wait_text)

    # Получаем список строк из логики
    debts_list = logic.calculate_debts(expenses, participants)

    result_text = ""
    if not debts_list:
        # Если список пуст — берем фразу "Никто не должен" из словаря
        result_text = await get_msg(chat_id, "no_debts")
    else:
        # Если есть долги — соединяем их в один текст
        result_text = "\n".join(debts_list)

    header_tmpl = await get_msg(chat_id, "balance_header")
    
    await message.answer(header_tmpl.format(text=result_text), parse_mode="HTML")

@dp.message(Command("clear"))
async def clear_history(message: types.Message):
    await db.clear_group_data(message.chat.id)
    text = await get_msg(message.chat.id, "cleared")
    # Добавили parse_mode="HTML", чтобы теги заработали
    await message.answer(text, parse_mode="HTML")

# --- ЗАПУСК ---

async def main():
    print("Бот запущен и готов работать!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())