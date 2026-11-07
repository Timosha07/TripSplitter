# TripSplitter

Telegram expense splitting bot for groups. Python 3.12, aiogram 3, PostgreSQL.
Russian, Kazakh and English interfaces.

## Features

- Exact KZT amounts, stored as integer hundredths; deterministic remainder distribution.
- Telegram IDs identify people. Each expense keeps its shares: joining later never changes old debts.
- Foreign currencies, saved original amount and conversion rate, one-hour rate cache.
- Expense history, editing, deletion and undo with author/admin permissions.
- Partial repayments applied only after the recipient confirms receipt.
- Duplicate protection, transactional writes and administrator-confirmed clear.

## Docker Compose

1. Clone `https://github.com/Timosha07/TripSplitter.git` and enter the repository.
2. Copy `.env.example` to `.env`. Set `BOT_TOKEN` from BotFather and a new
   `POSTGRES_PASSWORD` (a long random alphanumeric password avoids URL escaping issues).
3. Start Docker, then `docker compose up --build -d`.
4. Inspect startup with `docker compose logs -f bot`.

Compose starts PostgreSQL, waits for readiness, runs schema migration, then starts polling.
Database files persist in a named volume. Run only one polling process per token.
Allow the bot to receive commands in your group. Members should `/join` before expenses.

## Local setup

Create a dedicated PostgreSQL database, then:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Copy .env.example to .env; set BOT_TOKEN and DATABASE_URL.
python migrate.py
python bot.py
```

`DATABASE_URL` is `postgresql://user:password@host:5432/database`; URL-encode special
characters in credentials. Migration is required before starting the bot. An old
`expenses` table stops migration: see [MIGRATION.md](MIGRATION.md).

## Commands

| Command | Behavior |
| --- | --- |
| `/join` | Join future expenses; refresh display name and username |
| `/paid 100,50 taxi` | Add expense; comma or decimal point accepted |
| `/paid 10 USD lunch except @bob` | Convert and exclude registered participants |
| `/balance` or `/stop` | Suggested debt transfers |
| `/expenses` or `/expenses 2` | History cards, newest first, five per page |
| `/edit 12 1500 taxi` | Replace amount/description, retain original participants |
| `/delete 12` | Delete expense as author or administrator |
| `/undo` | Delete your latest active expense |
| `/repay @alice 200` | Report a pending repayment in KZT |
| Reply to recipient with `/repay 200` | Report repayment without a username |
| `/transfers` | Repayment history and pending confirmations |
| `/lang` | Language; administrators control group language |
| `/clear` | Administrator confirmation to clear the chat ledger |

Balance buttons create pending records; they do **not** send money. Only the recipient
can confirm or reject them. Repeated confirmation never applies a payment twice.
A mistaken confirmed transfer can currently be counteracted by a confirmed reverse transfer.

Currencies: KZT, USD, EUR, GBP, RUB, TRY, AED, CNY, JPY, THB, GEL, UZS, KGS.
Conversion uses Yahoo Finance's latest available closing value, not a guaranteed live
bank rate. Failed conversions do not save an expense. Editing a foreign-currency amount
uses the current cached rate; untouched expenses retain their saved rate.
Amounts must be positive with at most 10 input digits and 2 fractional digits.
Remainders are assigned in Telegram ID order. Debt suggestions are deterministic and
greedy, without a guarantee of the globally smallest number of transfers.
Names/descriptions are HTML-escaped. Username lookup reflects the latest registration;
use a reply for repayments when a username changed.

## Tests

```sh
pip install -r requirements-dev.txt
python -m pytest -q
```

Set `TEST_DATABASE_URL` to a disposable, dedicated PostgreSQL database for integration
tests. They apply migrations, verify concurrent writes and rollback, then remove their
test ledger. CI uses PostgreSQL 16. Telegram handler tests use simulated messages.

## Storage and limits

`ts_schema` versions the schema. `ts_ledgers` keeps one JSONB ledger per chat; writes
lock that row inside a transaction. All money is integer hundredths. Full ledger reads
and writes grow with history: large deployments should normalize expenses and transfers
into indexed tables before adding large archives and analytics. Deleted expenses and
edit history remain until explicit clear. Clear preserves replay markers and increasing
IDs so previous events cannot recreate deleted expenses or target newly created records.

Next: separate trips, custom shares, guided input and analytics. See [ROADMAP.md](ROADMAP.md).
