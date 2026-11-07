import asyncio
from contextlib import asynccontextmanager
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock
import bot
import domain as d

class MemoryStore:
    def __init__(self):
        self.state = d.empty()
    async def read(self, chat):
        return deepcopy(self.state)
    @asynccontextmanager
    async def edit(self, chat):
        state = deepcopy(self.state)
        yield state
        self.state = state

def message(text, user=1, mid=1):
    return SimpleNamespace(text=text, message_id=mid, from_user=SimpleNamespace(id=user, username=f'user{user}', full_name=f'User {user}'),
        sender_chat=None, reply_to_message=None, chat=SimpleNamespace(id=-1, type='group'),
        answer=AsyncMock(), edit_reply_markup=AsyncMock(),
        bot=SimpleNamespace(get_chat_member=AsyncMock(return_value=SimpleNamespace(status='member'))))

def query(msg, data, user):
    return SimpleNamespace(message=msg, from_user=SimpleNamespace(id=user), data=data, answer=AsyncMock())

def test_complete_user_flow():
    async def run():
        store = MemoryStore()
        await bot.command(message('/join', 1, 1), store)
        await bot.command(message('/join', 2, 2), store)
        paid = message('/paid@TripSplitterBot 100,50 <taxi>', 1, 3)
        await bot.command(paid, store)
        assert '&lt;taxi&gt;' in paid.answer.call_args.args[0]
        await bot.command(paid, store)
        assert len(store.state['expenses']) == 1
        await bot.command(message('/join', 3, 4), store)
        assert d.debts(store.state) == [('2', '1', 5025)]
        await bot.command(message('/edit 1 120 taxi', 2, 5), store)
        assert store.state['expenses'][0]['amount'] == 10050
        await bot.command(message('/edit 1 120 taxi', 1, 6), store)
        assert d.debts(store.state) == [('2', '1', 6000)]
        await bot.command(message('/repay @user1 20', 2, 7), store)
        assert d.debts(store.state) == [('2', '1', 6000)]
        t = store.state['transfers'][0]
        msg = message('', 1, 8)
        await bot.callback(query(msg, f"confirm:{t['id']}", 2), store)
        assert store.state['transfers'][0]['status'] == 'pending'
        await bot.callback(query(msg, f"confirm:{t['id']}", 1), store)
        assert d.debts(store.state) == [('2', '1', 4000)]
        await bot.callback(query(msg, f"confirm:{t['id']}", 1), store)
        assert d.debts(store.state) == [('2', '1', 4000)]
        await bot.command(message('/expenses', 2, 9), store)
        await bot.command(message('/transfers', 2, 10), store)
        await bot.callback(query(msg, 'delete:1:0', 1), store)
        assert not store.state['expenses'][0]['deleted']  # stale undo after edit
        await bot.callback(query(msg, 'pay:2:1:4000:0', 2), store)
        assert len(store.state['transfers']) == 2
        await bot.callback(query(msg, 'pay:2:1:4000:0', 2), store)
        assert len(store.state['transfers']) == 2
        store.state['generation'] = 1
        await bot.callback(query(message('', mid=99), 'pay:2:1:4000:0', 2), store)
        assert len(store.state['transfers']) == 2
    asyncio.run(run())

def test_clear_requires_admin_and_current_snapshot():
    async def run():
        store = MemoryStore()
        await bot.command(message('/join', 1), store)
        msg = message('/clear', 1, 2)
        await bot.command(msg, store)
        assert msg.answer.call_args.args[0] == bot.tr(store.state, 'permission')
        msg.bot.get_chat_member.return_value.status = 'administrator'
        await bot.command(msg, store)
        data = msg.answer.call_args.kwargs['reply_markup'].inline_keyboard[0][0].callback_data
        await bot.command(message('/join', 2, 3), store)
        await bot.callback(query(msg, data, 1), store)
        assert len(store.state['users']) == 2
        await bot.command(msg, store)
        data = msg.answer.call_args.kwargs['reply_markup'].inline_keyboard[0][0].callback_data
        await bot.callback(query(msg, data, 1), store)
        assert not store.state['users']
        assert store.state['generation'] == 1
    asyncio.run(run())
