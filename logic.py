def calculate_debts(expenses, joined_users):
    # 1. Собираем всех участников
    participants = set(joined_users) 
    
    for row in expenses:
        participants.add(row.payer_name)

    if not participants:
        return [] # Возвращаем пустой список, а не текст

    # 2. Считаем баланс
    balances = {user: 0.0 for user in participants}

    for row in expenses:
        payer = row.payer_name
        amount = float(row.amount)
        excluded = row.excluded_users.split(",") if row.excluded_users else []
        
        balances[payer] += amount

        share_participants = [p for p in participants if p not in excluded]
        
        if not share_participants:
            continue

        share_amount = amount / len(share_participants)

        for p in share_participants:
            balances[p] -= share_amount

    # 3. Минимизация транзакций
    debtors = []
    creditors = []

    for person, amount in balances.items():
        if amount < -0.01: debtors.append([person, amount])
        if amount > 0.01:  creditors.append([person, amount])

    report = []
    i = 0
    j = 0
    while i < len(debtors) and j < len(creditors):
        debtor_name, debt_val = debtors[i]
        creditor_name, credit_val = creditors[j]
        amount = min(abs(debt_val), credit_val)
        
        # Тут текст "KZT" оставляем, это валюта базы
        report.append(f"🔴 <b>{debtor_name}</b> ➡️ 🟢 <b>{creditor_name}</b>: {int(amount)} KZT")
        
        debtors[i][1] += amount
        creditors[j][1] -= amount

        if abs(debtors[i][1]) < 0.01: i += 1
        if creditors[j][1] < 0.01: j += 1

    return report # Просто возвращаем список строк (или пустой список)