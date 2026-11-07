from html import escape

LABELS = {
 'amount': ('Нужна положительная сумма с точностью до 0,01.', 'Enter a positive amount, up to 2 decimals.', 'Оң соманы енгізіңіз, үтірден кейін 2 таңбаға дейін.'),
 'input': ('Неверный формат. /help', 'Invalid format. /help', 'Пішім қате. /help'),
 'currency': ('Валюта не поддерживается.', 'Unsupported currency.', 'Валюта қолдау таппайды.'),
 'participants': ('Проверьте участников (/join). Нельзя исключить всех или переводить себе.', 'Check participants (/join). Cannot exclude everyone or pay yourself.', 'Қатысушыларды тексеріңіз (/join). Барлығын алып тастауға не өзіңізге аударуға болмайды.'),
 'duplicate': ('Уже обработано.', 'Already processed.', 'Орындалған.'),
 'permission': ('Недостаточно прав.', 'Permission denied.', 'Рұқсат жоқ.'),
 'missing': ('Запись не найдена.', 'Record not found.', 'Жазба табылмады.'),
 'rate': ('Курс недоступен. Расход не сохранён.', 'Rate unavailable. Expense not saved.', 'Курс алынбады. Шығын сақталмады.'),
 'joined': ('Вы участвуете в новых расходах.', 'You joined future expenses.', 'Сіз жаңа шығындарға қосылдыңыз.'),
 'saved': ('Сохранено', 'Saved', 'Сақталды'),
 'deleted': ('Удалено.', 'Deleted.', 'Жойылды.'),
 'edited': ('Изменено.', 'Updated.', 'Өзгертілді.'),
 'empty': ('Записей нет.', 'No records.', 'Жазбалар жоқ.'),
 'balanced': ('Долгов нет.', 'No debts.', 'Қарыз жоқ.'),
 'undo': ('Отменить расход', 'Undo expense', 'Шығынды болдырмау'),
 'confirm': ('Подтвердить получение', 'Confirm receipt', 'Алуды растау'),
 'reject': ('Отклонить', 'Reject', 'Қабылдамау'),
 'pending': ('Ожидает подтверждения получателя', 'Awaiting recipient confirmation', 'Алушының растауын күтуде'),
 'confirmed': ('Получение подтверждено', 'Receipt confirmed', 'Алу расталды'),
 'rejected': ('Отклонено', 'Rejected', 'Қабылданбады'),
 'clear': ('Удалить расходы, возвраты и участников этого чата?', 'Delete expenses, repayments and participants in this chat?', 'Осы чаттағы шығындар, қайтарымдар мен қатысушылар жойылсын ба?'),
 'yes': ('Да, очистить', 'Yes, clear', 'Иә, тазалау'),
 'cleared': ('История очищена.', 'History cleared.', 'Тарих тазаланды.'),
 'cancel': ('Отмена', 'Cancel', 'Болдырмау'),
 'next': ('Далее', 'Next', 'Келесі'),
 'previous': ('Назад', 'Previous', 'Алдыңғы'),
 'language': ('Язык сохранён.', 'Language saved.', 'Тіл сақталды.'),
 'stale': ('Данные изменились. Повторите команду.', 'Data changed. Run the command again.', 'Деректер өзгерді. Команданы қайталаңыз.'),
 'help': (
  '/join — участие в новых расходах\n/paid 100,50 такси\n/paid 10 USD обед except @user\n/balance — долги\n/expenses — история\n/edit ID сумма [валюта] описание\n/delete ID — удалить свою трату\n/undo — отменить последнюю свою трату\n/repay @user 200 — возврат KZT; можно ответить получателю: /repay 200\n/transfers — история возвратов\n/lang — язык\n/clear — очистка с подтверждением администратора',
  '/join — join future expenses\n/paid 100.50 taxi\n/paid 10 USD lunch except @user\n/balance — debts\n/expenses — history\n/edit ID amount [currency] description\n/delete ID — delete your expense\n/undo — undo your latest expense\n/repay @user 200 — repay KZT; or reply to recipient: /repay 200\n/transfers — repayments\n/lang — language\n/clear — clear with administrator confirmation',
  '/join — жаңа шығындарға қатысу\n/paid 100,50 такси\n/paid 10 USD түскі ас except @user\n/balance — қарыздар\n/expenses — тарих\n/edit ID сома [валюта] сипаттама\n/delete ID — өз шығынын жою\n/undo — соңғы өз шығынын болдырмау\n/repay @user 200 — KZT қайтару; немесе алушыға жауап: /repay 200\n/transfers — қайтарымдар\n/lang — тіл\n/clear — әкімші растауымен тазалау'),
}

def tr(state, key):
    return LABELS[key][{'ru': 0, 'en': 1, 'kz': 2}.get(state['language'], 0)]

def name(state, uid):
    return escape(state['users'].get(str(uid), {}).get('name', str(uid)))
