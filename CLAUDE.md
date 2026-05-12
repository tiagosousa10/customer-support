# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

This is an early-stage scaffold for an **AI copilot for customer support agents** (RAG + memory + LLM drafting). Most of the package layout exists but is currently empty (`api/`, `services/`, `integrations/`, and several `repositories/sqlite/` modules are placeholder `__init__.py` files or empty files). Treat the directory structure as the *intended* architecture rather than implemented behavior — when adding code, slot it into the existing layered layout instead of inventing new top-level modules.

`README.md` is currently a single-line stub; do not assume it documents anything.

## Environment & commands

- **Python**: requires `3.14` (pinned in `.python-version`).
- **Package manager**: `uv` (lockfile is `uv.lock`).
- **Install / sync deps**: `uv sync`
- **Run entry script**: `uv run python main.py` (currently just prints a hello message)
- **Notebook experiments**: `uv run jupyter lab notebooks/experiments.ipynb` (the notebook is the live sketchpad for wiring mem0 + Groq + ChromaDB before code lands in the package)
- **Add a dependency**: `uv add <pkg>` (do not edit `pyproject.toml` by hand if avoidable — let `uv` update `uv.lock`)

There is no test suite, lint config, or build step configured yet. `tests/` exists but is empty.

## Package name (read this before importing)

The Python package is `customer__support_agent` — note the **double underscore** between `customer` and `support`. All intra-project imports use this exact spelling, e.g.:

```python
from customer__support_agent.core.settings import get_settings, ensure_directories
```

Do not "fix" this to a single underscore — it would break every existing import and the `uv` project metadata.

## Architecture

The intended layering, top-down:

- `customer__support_agent/api/` — HTTP API surface (planned; empty). Settings expose `api_host`/`api_port` (default `0.0.0.0:8000`) and a `dashboard_api_url`, suggesting a FastAPI-style service + separate dashboard frontend.
- `customer__support_agent/services/` — orchestration: ticket → retrieval → draft generation. Empty.
- `customer__support_agent/integrations/` — external providers (Groq LLM, mem0, embeddings). Empty; experiment code currently lives in `notebooks/experiments.ipynb`.
- `customer__support_agent/repositories/sqlite/` — persistence. `base.py` owns connection lifecycle + schema bootstrap; per-entity modules (`customer.py`, `tickets.py`, `drafts.py`) hold CRUD. `tickets.py` and `drafts.py` are currently empty.
- `customer__support_agent/schemas/api.py` — Pydantic request/response models for the planned API, including `StructuredDraftContext` which is the canonical shape of "what context fed the draft" (memory hits, knowledge hits, tool calls, signals, highlights). When you generate or consume draft context, conform to this schema.
- `customer__support_agent/core/settings.py` — single source of truth for config and paths.

### Three persistence stores (don't confuse them)

The system maintains three distinct stores, all rooted at `data/` (auto-created by `ensure_directories()`):

1. `data/support.db` — SQLite: customers, tickets, drafts (relational, transactional).
2. `data/chroma_rag/` — ChromaDB collection for the **knowledge base** (RAG retrieval over docs in `knowledge_base/`).
3. `data/chroma_mem0/` — ChromaDB collection backing **mem0** (per-customer conversational memory).

Settings exposes resolved paths via `settings.db_file`, `settings.chroma_rag_path()`, `settings.chroma_mem0_path`, `settings.knowledge_base_path`. Note the asymmetry: `chroma_rag_path` is a method, the others are properties — match the existing call style when extending.

### Settings pattern

- `get_settings()` is `@lru_cache`-d → a single `Settings` instance per process.
- Paths in `Settings` are stored **relative** (e.g. `Path("data/support.db")`) and resolved against `workspace_dir` via `settings.resolve(...)`. Always go through `resolve()` (or a property that wraps it) rather than treating raw fields as filesystem paths.
- `ensure_directories(settings)` is idempotent and is called inside `repositories/sqlite/base.connect()` — meaning any code path that opens a DB connection will also materialize the data directories. If you add a new store, add it to `ensure_directories()`.
- Env vars are loaded from `.env` (via `pydantic-settings`) with `extra="ignore"`. Known keys: `GROQ_API_KEY` (required for the LLM/mem0 path), `OPENAI_API_KEY`, `GOOGLE_API_KEY` (declared but unused so far).

### SQLite conventions

- Every repository method opens its own connection via `connect()` (no shared connection pool). Transactions are therefore scoped per-method; if you need atomicity across operations, open one `with connect() as conn:` and pass `conn` down.
- Connections use `row_factory = sqlite3.Row` and `PRAGMA foreign_keys = ON`. Use `row_to_dict(row)` from `base.py` to convert before returning out of the repository layer.
- Schema is initialized by `init_db()` in `base.py` (idempotent `CREATE TABLE IF NOT EXISTS`). Call this once on startup; the existing code does not auto-invoke it.

## Known rough edges (do not silently "fix")

These are present in the current code; flag them explicitly with the user before changing, since some are likely WIP:

- `core/settings.py`: `workspace_dir : Path = Path(__file__).resolve().parent[2]` — `Path.parent` is not indexable; this should be `.parents[2]`. Will raise on first import.
- `pyproject.toml` lists `dotenv` but not `pydantic-settings`, even though `core/settings.py` imports `pydantic_settings`. Similarly `EmailStr` (used in `schemas/api.py`) requires the `email-validator` extra. Both need to be added before the package can be imported.
- `repositories/sqlite/customer.py`: the refresh `SELECT` after an UPDATE is missing its parameter binding (`conn.execute("SELECT ... WHERE email = ?")` with no second arg). `get_by_id` / `get_by_email` are stubs.

## Secrets

`.env` is currently **not** in `.gitignore` (`.gitignore` is empty) and the working tree has a real `GROQ_API_KEY` value in it. Do not commit `.env`. If you touch `.gitignore`, add `.env`, `.venv/`, `data/`, and `__pycache__/` at minimum.
