# Spendly development guidelines

The maintained guidance for Claude is in [.claude/CLAUDE.md](.claude/CLAUDE.md). Refer to that file for setup, architecture, current route status, testing, and implementation conventions.

Follow the [spec-driven workflow](instructions.md): review the specification, review the implementation plan, implement the scoped change, and validate against acceptance criteria.

Database setup, registration, login/logout, and the database-backed profile are implemented. Expense creation, editing, and deletion remain placeholders. Database query helpers live in `database/queries.py`; connection, schema, seeding, and authentication helpers live in `database/db.py`.

Use `python -m pytest tests/` for the self-contained suite. The separate root-level smoke script requires a live server and an additional dependency; see the [README](README.md#tests-and-validation).
