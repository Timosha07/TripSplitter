"""Pure ledger operations. All stored money is integer hundredths of KZT."""
from decimal import Decimal, ROUND_HALF_UP
import re
from datetime import datetime, timezone

CURRENCIES = {'KZT', 'USD', 'EUR', 'GBP', 'RUB', 'TRY', 'AED', 'CNY', 'JPY', 'THB', 'GEL', 'UZS', 'KGS'}

class Invalid(ValueError):
    pass

def now():
    return datetime.now(timezone.utc).isoformat()

def amount(value):
    if not re.fullmatch(r'\d{1,10}(?:[.,]\d{1,2})?', value):
        raise Invalid('amount')
    result = Decimal(value.replace(',', '.'))
    if result <= 0:
        raise Invalid('amount')
    return result

def cents(value):
    result = int((value * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    if not 0 < result <= 10**14:
        raise Invalid('amount')
    return result

def money(value):
    return f'{Decimal(value) / 100:.2f}'

def parse(text):
    parts = text.strip().split(maxsplit=1)
    value = amount(parts[0] if parts else '')
    rest = parts[1] if len(parts) > 1 else ''
    code = 'KZT'
    first = rest.split(maxsplit=1)
    if first and first[0].upper() in CURRENCIES:
        code = first[0].upper()
        rest = first[1] if len(first) > 1 else ''
    elif first and re.fullmatch('[A-Z]{3}', first[0]):
        raise Invalid('currency')
    split = re.split(r'\s*\bexcept\b\s*', rest, maxsplit=1, flags=re.I)
    description = split[0].strip() or '—'
    excluded = split[1].split() if len(split) > 1 else []
    if len(description) > 500 or any(not re.fullmatch(r'@[A-Za-z0-9_]+', x) for x in excluded):
        raise Invalid('input')
    if len(split) > 1 and not excluded:
        raise Invalid('input')
    return value, code, description, [x.lower() for x in excluded]

def empty():
    return dict(users={}, expenses=[], transfers=[], seen={}, next_id=1, language='ru', generation=0)

def register(state, user_id, name, username=None):
    state['users'][str(user_id)] = {'name': name, 'username': username.lower() if username else None}

def shares(total, users):
    users = sorted(set(users), key=int)
    if not users:
        raise Invalid('participants')
    quotient, remainder = divmod(total, len(users))
    return {user: quotient + (i < remainder) for i, user in enumerate(users)}

def add(state, key, payer, total, original, code, rate, description, excluded):
    if key in state['seen']:
        raise Invalid('duplicate')
    usernames = {u['username']: uid for uid, u in state['users'].items() if u['username']}
    if any(x[1:] not in usernames for x in excluded):
        raise Invalid('participants')
    omit = {usernames[x[1:]] for x in excluded}
    portions = shares(total, set(state['users']) - omit)
    item = dict(id=state['next_id'], payer=str(payer), amount=total, original=str(original),
                currency=code, rate=str(rate), rate_at=now(), description=description,
                shares=portions, created_at=now(), deleted=False, revision=0)
    state['next_id'] += 1
    state['expenses'].append(item)
    state['seen'][key] = item['id']
    return item

def expense(state, item_id):
    item = next((x for x in state['expenses'] if x['id'] == item_id and not x['deleted']), None)
    if not item:
        raise Invalid('missing')
    return item

def change(state, item_id, actor, admin=False, updated=None):
    item = expense(state, item_id)
    if str(actor) != item['payer'] and not admin:
        raise Invalid('permission')
    if updated is None:
        item['deleted'] = True
    else:
        total, original, code, rate, description = updated
        item.setdefault('history', []).append({k: v for k, v in item.items() if k != 'history'})
        item.update(amount=total, original=str(original), currency=code, rate=str(rate),
                    rate_at=now(), description=description, shares=shares(total, item['shares']))
    item['revision'] += 1
    return item

def transfer(state, key, sender, recipient, total):
    sender, recipient = str(sender), str(recipient)
    if key in state['seen']:
        raise Invalid('duplicate')
    if sender == recipient or sender not in state['users'] or recipient not in state['users']:
        raise Invalid('participants')
    item = dict(id=state['next_id'], sender=sender, recipient=recipient, amount=total,
                status='pending', created_at=now())
    state['next_id'] += 1
    state['transfers'].append(item)
    state['seen'][key] = item['id']
    return item

def confirm(state, item_id, actor, accept):
    item = next((x for x in state['transfers'] if x['id'] == item_id), None)
    if not item:
        raise Invalid('missing')
    if str(actor) != item['recipient']:
        raise Invalid('permission')
    if item['status'] != 'pending':
        raise Invalid('duplicate')
    item.update(status='confirmed' if accept else 'rejected', confirmed_at=now())
    return item

def balances(state):
    result = dict.fromkeys(state['users'], 0)
    for item in state['expenses']:
        if item['deleted']:
            continue
        result[item['payer']] += item['amount']
        for uid, value in item['shares'].items():
            result[uid] -= value
    for item in state['transfers']:
        if item['status'] == 'confirmed':
            result[item['sender']] += item['amount']
            result[item['recipient']] -= item['amount']
    return result

def debts(state):
    result = balances(state)
    debtors = [[uid, -value] for uid, value in sorted(result.items()) if value < 0]
    creditors = [[uid, value] for uid, value in sorted(result.items()) if value > 0]
    output = []
    for debtor in debtors:
        for creditor in creditors:
            value = min(debtor[1], creditor[1])
            if value:
                output.append((debtor[0], creditor[0], value))
                debtor[1] -= value
                creditor[1] -= value
    return output
