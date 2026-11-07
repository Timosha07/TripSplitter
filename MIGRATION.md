# Existing installations

The original repository had no schema or migrations. Usernames/names were identifiers,
and historical participants were computed from the group's current membership.
Telegram IDs and historical shares cannot be reliably inferred from that data.

Migration refuses databases containing `public.expenses`. It never deletes old records
or guesses identity mappings. Run v2 in a dedicated database. Migration is repeatable.

Before switching a working bot:

1. Stop its polling process. Back up the database with `pg_dump` and verify restoration
   into a separate database. Keep the old code and configuration for rollback.
2. Export old history and settle or record its closing balances.
3. Create a new v2 database, migrate, have members `/join`, and start a new ledger.
4. If unsettled history must be imported, postpone switching: inspect the real schema,
   explicitly map names to Telegram IDs and agree the shares of each old expense.
   Implement and validate a dedicated importer on a copy. This release does not include
   an automatic legacy importer.

Rollback requires stopping v2 and restarting the old deployment against its original
database. Reconcile any new v2 activity first; it is not automatically copied backwards.

Fresh installations run `python migrate.py` before `python bot.py`, or use Compose.
Future schema versions must add explicit migration steps, not rewrite version numbers.
