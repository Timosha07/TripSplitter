MESSAGES = {
    "ru": {
        "welcome": (
            "<b>👋 Привет! Я — TripSplitter.</b>\n"
            "Я помогу вашей компании не переругаться из-за денег в поездке.\n\n"
            "<b>📜 Что я умею:</b>\n\n"
            "💸 <b>/paid [сумма] [валюта] [трата]</b>\n"
            "Добавить расход. Я сам переведу валюту в тенге.\n"
            "• <i>Пример:</i> <code>/paid 5000 такси</code>\n"
            "• <i>Пример:</i> <code>/paid 10 USD магнитики</code>\n"
            "• <i>Исключить кого-то:</i> <code>/paid 2000 ужин except @oleg</code>\n\n"
            "➕ <b>/join</b>\n"
            "Нажми, чтобы участвовать в делении счета (даже если сам ничего не платил).\n\n"
            "🧮 <b>/stop</b>\n"
            "Посчитать, кто кому сколько должен.\n\n"
            "🌍 <b>/lang</b>\n"
            "Сменить язык (Русский / Qazaqsha / English).\n\n"
            "🧹 <b>/clear</b> — Удалить все записи и начать заново."
        ),
        "paid_header": "✅ <b>{name}</b> заплатил <b>{amount} KZT</b>",
        "paid_cur": "\n💱 Конвертация: {original} x {rate:.2f}",
        "paid_desc": "\n📝 Описание: {desc}",
        "join_msg": "👋 <b>{name}</b> в игре! Теперь расходы делятся и на тебя.",
        "calc_start": "🧮 Считаю долги с учетом всех участников...",
        "balance_header": "📊 <b>ИТОГИ ПОЕЗДКИ:</b>\n\n{text}",
        "group_empty": "🤷‍♂️ Группа пуста. Добавьте трат или нажмите /join.",
        "cleared": "🧹 <b>История очищена!</b>",
        "choose_lang": "🌍 Выберите язык / Til tańdańyz / Choose language:",
        "lang_set": "🇷🇺 Язык изменен на Русский!",
        "err_no_sum": "❌ Не понял сумму. Пример: /paid 5000 обед",
        "err_no_rate": "⚠️ Не нашел курс для {currency}. Проверь написание (USD, EUR).",
        "no_debts": "🎉 <b>Никто никому ничего не должен!</b>"
    },
    "kz": {
        "welcome": (
            "<b>👋 Сәлем! Мен — TripSplitter-мін.</b>\n"
            "Саяхатта ақша санауға көмектесемін.\n\n"
            "<b>📜 Менің командаларым:</b>\n\n"
            "💸 <b>/paid [сома] [валюта] [сипаттама]</b>\n"
            "Шығынды қосу. Валютаны теңгеге өзім аударамын.\n"
            "• <i>Мысалы:</i> <code>/paid 5000 такси</code>\n"
            "• <i>Мысалы:</i> <code>/paid 10 USD көрімдік</code>\n"
            "• <i>Біреуді қоспау:</i> <code>/paid 2000 кешкі ас except @алмас</code>\n\n"
            "➕ <b>/join</b>\n"
            "Есепке қосылу (егер сіз ештеңе төлемесеңіз де).\n\n"
            "🧮 <b>/stop</b>\n"
            "Қорытынды есептеу: кім кімге қанша қарыз.\n\n"
            "🌍 <b>/lang</b>\n"
            "Тілді өзгерту (Русский / Qazaqsha / English).\n\n"
            "🧹 <b>/clear</b> — Барлық жазбаларды өшіру."
        ),
        "paid_header": "✅ <b>{name}</b> төледі: <b>{amount} KZT</b>",
        "paid_cur": "\n💱 Валюта: {original} x {rate:.2f}",
        "paid_desc": "\n📝 Сипаттама: {desc}",
        "join_msg": "👋 <b>{name}</b> қосылды! Енді шығындар сізге де бөлінеді.",
        "calc_start": "🧮 Барлық қатысушыларды ескеріп санап жатырмын...",
        "balance_header": "📊 <b>ҚОРЫТЫНДЫ:</b>\n\n{text}",
        "group_empty": "🤷‍♂️ Топ бос. Шығын қосыңыз немесе /join басыңыз.",
        "cleared": "🧹 <b>Тарих тазаланды!</b>",
        "choose_lang": "🌍 Тіл таңдаңыз:",
        "lang_set": "🇰🇿 Тіл Қазақшаға ауыстырылды!",
        "err_no_sum": "❌ Сома түсініксіз. Мысалы: /paid 5000 түскі ас",
        "err_no_rate": "⚠️ {currency} курсы табылмады.",
        "no_debts": "🎉 <b>Ешкім ешкімге қарыз емес, дәл келді!</b>"
    },
    "en": {
        "welcome": (
            "<b>👋 Hi! I am TripSplitter.</b>\n"
            "I help you split bills effortlessly.\n\n"
            "<b>📜 My commands:</b>\n\n"
            "💸 <b>/paid [amount] [currency] [item]</b>\n"
            "Add an expense. I convert currencies to KZT automatically.\n"
            "• <i>Example:</i> <code>/paid 5000 taxi</code>\n"
            "• <i>Example:</i> <code>/paid 10 USD magnets</code>\n"
            "• <i>Exclude someone:</i> <code>/paid 2000 dinner except @almas</code>\n\n"
            "➕ <b>/join</b>\n"
            "Join the bill splitting (even if you haven't paid anything).\n\n"
            "🧮 <b>/stop</b>\n"
            "Calculate final debts (who owes whom).\n\n"
            "🌍 <b>/lang</b>\n"
            "Change language.\n\n"
            "🧹 <b>/clear</b> — Delete all history and start over."
        ),
        "paid_header": "✅ <b>{name}</b> paid <b>{amount} KZT</b>",
        "paid_cur": "\n💱 Conversion: {original} x {rate:.2f}",
        "paid_desc": "\n📝 Description: {desc}",
        "join_msg": "👋 <b>{name}</b> joined! Expenses are now split with you.",
        "calc_start": "🧮 Calculating debts...",
        "balance_header": "📊 <b>RESULTS:</b>\n\n{text}",
        "group_empty": "🤷‍♂️ Group is empty. Add expenses or type /join.",
        "cleared": "🧹 <b>History cleared!</b>",
        "choose_lang": "🌍 Choose language:",
        "lang_set": "🇺🇸 Language set to English!",
        "err_no_sum": "❌ Invalid amount. Example: /paid 5000 lunch",
        "err_no_rate": "⚠️ Rate not found for {currency}.",
        "no_debts": "🎉 <b>No one owes anything!</b>"
    }
}