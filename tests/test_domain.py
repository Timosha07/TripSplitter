from decimal import Decimal
import random
import pytest
import domain as d

def ledger():
    s = d.empty()
    d.register(s, 1, 'Alice', 'alice')
    d.register(s, 2, 'Bob', 'bob')
    return s

def add(s, value=10050, key='1', excluded=None):
    return d.add(s, key, 1, value, Decimal(value)/100, 'KZT', Decimal(1), '<taxi>', excluded or [])

@pytest.mark.parametrize('text', ['-1', '0', 'NaN', 'inf', '1e5', '1.234', '1,2.3', '', '9999999999999999'])
def test_invalid_amount(text):
    with pytest.raises(d.Invalid):
        d.amount(text)

def test_parsing():
    assert d.parse('100 taxi')[:3] == (Decimal('100'), 'KZT', 'taxi')
    assert d.parse('10,50 кофе')[0] == Decimal('10.50')
    assert d.parse('10 usd lunch EXCEPT @Bob') == (Decimal(10), 'USD', 'lunch', ['@bob'])
    with pytest.raises(d.Invalid):
        d.parse('10 XYZ food')
    with pytest.raises(d.Invalid):
        d.parse('10 food except')

def test_exact_money_and_late_join():
    s = ledger()
    add(s)
    assert d.debts(s) == [('2', '1', 5025)]
    assert d.money(5025) == '50.25'
    d.register(s, 3, 'Carol')
    assert d.debts(s) == [('2', '1', 5025)]
    d.register(s, 1, 'New Alice', 'newalice')
    assert d.debts(s) == [('2', '1', 5025)]

def test_conservation_randomized():
    rng = random.Random(41)
    for count in range(1, 30):
        s = d.empty()
        for user in range(count):
            d.register(s, user, 'same name')
        for i in range(10):
            total = rng.randrange(1, 100000)
            item = d.add(s, str(i), rng.randrange(count), total, str(total/100), 'KZT', '1', 'x', [])
            assert sum(item['shares'].values()) == total
        balances = d.balances(s)
        assert sum(balances.values()) == 0
        for sender, recipient, value in d.debts(s):
            balances[sender] += value
            balances[recipient] -= value
        assert set(balances.values()) == {0}

def test_exclusions_and_replay():
    s = ledger()
    with pytest.raises(d.Invalid):
        add(s, excluded=['@alice', '@bob'])
    with pytest.raises(d.Invalid):
        add(s, excluded=['@unknown'])
    add(s)
    with pytest.raises(d.Invalid, match='duplicate'):
        add(s)
    assert len(s['expenses']) == 1

def test_edit_permissions_preserve_members_and_delete():
    s = ledger()
    item = add(s)
    d.register(s, 3, 'Carol')
    with pytest.raises(d.Invalid, match='permission'):
        d.change(s, item['id'], 2)
    d.change(s, item['id'], 1, updated=(12001, '120.01', 'KZT', '1', 'edited'))
    assert set(item['shares']) == {'1', '2'}
    assert sum(item['shares'].values()) == 12001
    assert len(item['history']) == 1
    d.change(s, item['id'], 1)
    assert d.debts(s) == []

def test_partial_repayment_confirmed_only_by_recipient():
    s = ledger()
    add(s, 1000000)
    t = d.transfer(s, '2', 2, 1, 200000)
    assert d.debts(s) == [('2', '1', 500000)]
    with pytest.raises(d.Invalid, match='permission'):
        d.confirm(s, t['id'], 2, True)
    d.confirm(s, t['id'], 1, True)
    assert d.debts(s) == [('2', '1', 300000)]
    assert s['expenses'][0]['amount'] == 1000000
    with pytest.raises(d.Invalid, match='duplicate'):
        d.confirm(s, t['id'], 1, True)

def test_rejected_transfer_does_not_change_balance():
    s = ledger()
    add(s)
    t = d.transfer(s, '2', 2, 1, 500)
    d.confirm(s, t['id'], 1, False)
    assert d.debts(s) == [('2', '1', 5025)]

def test_translation_keys_and_html():
    from ui import LABELS, name
    assert all(len(values) == 3 and all(values) for values in LABELS.values())
    s = ledger()
    d.register(s, 1, '<b>A & B</b>')
    assert name(s, 1) == '&lt;b&gt;A &amp; B&lt;/b&gt;'
