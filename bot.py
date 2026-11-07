import asyncio
import hashlib
import json
import logging
from html import escape
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import domain as d
from config import bot_token, database_url
from currency import get_exchange_rate
from database import Store
from ui import tr, name

dp = Dispatcher()
log = logging.getLogger(__name__)

def keyboard(rows):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data=data) for label, data in row] for row in rows])

def remember(state, user):
    d.register(state, user.id, '@' + user.username if user.username else user.full_name, user.username)

def fingerprint(state):
    return hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()[:16]

async def is_admin(message, actor):
    if message.chat.type == 'private':
        return message.chat.id == actor
    member = await message.bot.get_chat_member(message.chat.id, actor)
    return member.status in ('creator', 'administrator')

async def send(message, text, **kwargs):
    return await message.answer(text, parse_mode='HTML', **kwargs)

async def converted(args):
    original, code, description, excluded = d.parse(args)
    try:
        rate = await get_exchange_rate(code)
    except Exception:
        log.warning('Exchange rate unavailable for %s', code)
        raise d.Invalid('rate') from None
    return d.cents(original * rate), original, code, rate, description, excluded

async def pending(message, state, item):
    await send(message, f"#{item['id']} {name(state, item['sender'])} → {name(state, item['recipient'])}: {d.money(item['amount'])} KZT\n{tr(state, item['status'])}", reply_markup=keyboard([[(tr(state, 'confirm'), f"confirm:{item['id']}"), (tr(state, 'reject'), f"reject:{item['id']}")]]))

async def history(message, state, page=0, transfers=False):
    items = list(reversed(state['transfers'] if transfers else [x for x in state['expenses'] if not x['deleted']]))
    page = max(0, min(page, max(0, (len(items)-1)//5)))
    if not items:
        return await send(message, tr(state, 'empty'))
    for item in items[page*5:page*5+5]:
        if transfers:
            if item['status'] == 'pending':
                await pending(message, state, item)
                continue
            body = f"#{item['id']} · {item['created_at'][:10]}\n{name(state, item['sender'])} → {name(state, item['recipient'])}: {d.money(item['amount'])} KZT\n{tr(state, item['status'])}"
            rows = []
        else:
            body = f"#{item['id']} · {item['created_at'][:10]}\n{name(state, item['payer'])}: {d.money(item['amount'])} KZT\n{escape(item['description'])}\n{escape(item['original'])} {item['currency']} × {escape(item['rate'])}"
            rows = [[(tr(state, 'undo'), f"delete:{item['id']}:{item['revision']}")]]
        await send(message, body, reply_markup=keyboard(rows) if rows else None)
    kind = 'transfers' if transfers else 'expenses'
    nav = []
    if page:
        nav.append((tr(state, 'previous'), f'{kind}:{page-1}'))
    if (page+1)*5 < len(items):
        nav.append((tr(state, 'next'), f'{kind}:{page+1}'))
    if nav:
        await send(message, f'{page+1}/{(len(items)+4)//5}', reply_markup=keyboard([nav]))

@dp.message(Command('start', 'help', 'join', 'paid', 'balance', 'stop', 'expenses', 'edit', 'delete', 'undo', 'repay', 'transfers', 'clear', 'lang'))
async def command(message, store: Store):
    state = await store.read(message.chat.id)
    if not message.from_user or message.sender_chat:
        return await send(message, tr(state, 'permission'))
    cmd, *tail = message.text.split(maxsplit=1)
    cmd = cmd.split('@')[0][1:]
    args = tail[0] if tail else ''
    actor, key = message.from_user.id, str(message.message_id)
    try:
        if cmd in ('start', 'help'):
            return await send(message, tr(state, 'help'))
        if cmd == 'lang':
            return await send(message, 'Русский / Қазақша / English', reply_markup=keyboard([[(label, f'lang:{code}')] for code, label in [('ru','Русский'), ('kz','Қазақша'), ('en','English')]]))
        if cmd == 'join':
            async with store.edit(message.chat.id) as state:
                remember(state, message.from_user)
            return await send(message, tr(state, 'joined'))
        if cmd == 'paid':
            values = await converted(args)
            async with store.edit(message.chat.id) as state:
                remember(state, message.from_user)
                item = d.add(state, key, actor, *values)
            return await send(message, f"{tr(state, 'saved')} #{item['id']}: {d.money(item['amount'])} KZT\n{escape(item['description'])}", reply_markup=keyboard([[(tr(state, 'undo'), f"delete:{item['id']}:0")]]))
        if cmd in ('expenses', 'transfers'):
            return await history(message, state, int(args or '1')-1, cmd == 'transfers')
        if cmd in ('balance', 'stop'):
            debts = d.debts(state)
            if not debts:
                return await send(message, tr(state, 'balanced'))
            for sender, recipient, value in debts:
                await send(message, f'{name(state, sender)} → {name(state, recipient)}: {d.money(value)} KZT', reply_markup=keyboard([[('✓ ' + d.money(value) + ' KZT', f"pay:{sender}:{recipient}:{value}:{state['generation']}")]]))
            return
        if cmd in ('edit', 'delete', 'undo'):
            admin = await is_admin(message, actor)
            updated = None
            if cmd == 'edit':
                item_id, new_args = args.split(maxsplit=1)
                values = await converted(new_args)
                if values[-1]:
                    raise d.Invalid('input')
                updated = values[:-1]
            elif cmd == 'delete':
                item_id = args
            else:
                item_id = next((x['id'] for x in reversed(state['expenses']) if x['payer'] == str(actor) and not x['deleted']), 0)
            async with store.edit(message.chat.id) as state:
                if key in state['seen']:
                    raise d.Invalid('duplicate')
                d.change(state, int(item_id), actor, admin, updated)
                state['seen'][key] = int(item_id)
            return await send(message, tr(state, 'edited' if updated else 'deleted'))
        if cmd == 'repay':
            parts = args.split()
            if message.reply_to_message and message.reply_to_message.from_user and len(parts) == 1:
                recipient, value = str(message.reply_to_message.from_user.id), parts[0]
            elif len(parts) == 2 and parts[0].startswith('@'):
                recipient = next((uid for uid, user in state['users'].items() if user['username'] == parts[0][1:].lower()), '')
                value = parts[1]
            else:
                raise d.Invalid('input')
            async with store.edit(message.chat.id) as state:
                item = d.transfer(state, key, actor, recipient, d.cents(d.amount(value)))
            return await pending(message, state, item)
        if cmd == 'clear':
            if not await is_admin(message, actor):
                raise d.Invalid('permission')
            return await send(message, tr(state, 'clear'), reply_markup=keyboard([[(tr(state, 'yes'), f'clear:{actor}:{fingerprint(state)}'), (tr(state, 'cancel'), 'cancel')]]))
    except d.Invalid as exc:
        await send(message, tr(state, str(exc)))
    except (ValueError, IndexError):
        await send(message, tr(state, 'input'))

@dp.callback_query(F.data)
async def callback(query, store: Store):
    if not query.message or not hasattr(query.message, 'answer'):
        return await query.answer()
    await query.answer()
    message, actor = query.message, query.from_user.id
    state = await store.read(message.chat.id)
    parts, action = query.data.split(':'), query.data.split(':')[0]
    try:
        if action == 'cancel':
            return await message.edit_reply_markup(reply_markup=None)
        if action in ('expenses', 'transfers'):
            return await history(message, state, int(parts[1]), action == 'transfers')
        admin = await is_admin(message, actor) if action in ('delete', 'clear', 'lang') else False
        async with store.edit(message.chat.id) as state:
            if action == 'lang':
                if not admin:
                    raise d.Invalid('permission')
                if parts[1] not in ('ru', 'kz', 'en'):
                    raise d.Invalid('input')
                state['language'], result = parts[1], 'language'
            elif action == 'delete':
                item = d.expense(state, int(parts[1]))
                if item['revision'] != int(parts[2]):
                    raise d.Invalid('stale')
                d.change(state, item['id'], actor, admin)
                result = 'deleted'
            elif action in ('confirm', 'reject'):
                result = d.confirm(state, int(parts[1]), actor, action == 'confirm')['status']
            elif action == 'pay':
                if str(actor) != parts[1]:
                    raise d.Invalid('permission')
                if int(parts[4]) != state['generation']:
                    raise d.Invalid('stale')
                sender, recipient, value = parts[1], parts[2], int(parts[3])
                if (sender, recipient, value) not in d.debts(state):
                    raise d.Invalid('stale')
                item = d.transfer(state, f'button:{message.message_id}', sender, recipient, value)
                result = None
            elif action == 'clear':
                if not admin or str(actor) != parts[1]:
                    raise d.Invalid('permission')
                if fingerprint(state) != parts[2]:
                    raise d.Invalid('stale')
                keep = {k: state[k] for k in ('seen', 'next_id', 'language')}
                generation = state['generation'] + 1
                state.clear()
                state.update(d.empty())
                state.update(keep, generation=generation)
                result = 'cleared'
            else:
                raise d.Invalid('input')
        if result is None:
            await pending(message, state, item)
        else:
            await send(message, tr(state, result))
        if action != 'lang':
            await message.edit_reply_markup(reply_markup=None)
    except d.Invalid as exc:
        await send(message, tr(state, str(exc)))
    except (ValueError, IndexError):
        await send(message, tr(state, 'input'))

@dp.errors()
async def error(event):
    log.error('Update failed: %s', type(event.exception).__name__)
    message = event.update.message or (event.update.callback_query.message if event.update.callback_query else None)
    if message and hasattr(message, 'answer'):
        await message.answer('Ошибка / Error / Қате. /help')
    return True

async def main():
    logging.basicConfig(level=logging.INFO)
    store, bot = Store(database_url()), Bot(bot_token())
    try:
        await store.open()
        await dp.start_polling(bot, store=store, close_bot_session=False)
    finally:
        await store.close()
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
