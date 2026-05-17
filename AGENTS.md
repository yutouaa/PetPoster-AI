# Repository Guidelines

## Project Structure & Module Organization

PetPoster AI has three product surfaces:

- `miniprogram/`: native WeChat mini program. Entry files are `app.js`, `app.json`, and `app.wxss`; pages are in `pages/`; icons and poster images are in `assets/`.
- `admin/`: Vue 3 + Vite + TypeScript admin console based on SoybeanAdmin Element Plus. Main source is `admin/src/`; Vite, ESLint, UnoCSS, and TypeScript configs live in the admin root.
- `api/`: FastAPI backend. App code is in `api/app/`, routes in `api/app/api/routes/`, database code in `api/app/db/`, and migrations in `api/alembic/versions/`.

The root `figma-petposter-mini-program-ui.js` is the Figma Plugin API design script.

## Build, Test, and Development Commands

- Mini program: open `miniprogram/` in WeChat DevTools.
- API, from `api/`: `uv sync`, `uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`, `uv run pytest`.
- API migrations, from `api/`: `uv run alembic upgrade head` or `uv run alembic revision --autogenerate -m "message"`.
- Admin, from `admin/`: `corepack enable`, `pnpm install`, `pnpm dev`, `pnpm build`.
- Admin checks, from `admin/`: `pnpm typecheck` and `pnpm lint`.
- Figma script syntax check: run `node --check figma-petposter-mini-program-ui.js`.

## Coding Style & Naming Conventions

Use Chinese for product copy and explanatory comments when practical; keep API paths, environment variables, and technical identifiers in English. Mini-program code stays native WXML/WXSS/JS; do not add Taro, uni-app, or TypeScript. Admin code follows SoybeanAdmin conventions, Vue single-file components, PascalCase component usage, and UnoCSS utilities. API code targets Python 3.12, FastAPI, SQLAlchemy, and Alembic.

## Testing Guidelines

Backend tests use `pytest`; place durable tests under `api/tests/test_*.py`, and keep root-level `test_*.py` only for short-lived smoke scripts. The admin package has no test script, so run `pnpm typecheck`, `pnpm lint`, and `pnpm build` before completing UI work. Validate mini-program changes in WeChat DevTools, especially WXML/WXSS compatibility.

## Commit & Pull Request Guidelines

This folder is not currently a Git repository, so no local commit history is available. For admin changes, prefer `pnpm commit`; package hooks verify commit messages and run pre-commit checks. PRs should name the affected surface (`miniprogram`, `admin`, or `api`), include check results, link related tasks, and attach screenshots or recordings for UI changes.

## Security & Agent Notes

Never commit real secrets, generated credentials, or production `.env` values. Change `ADMIN_PASSWORD` and `ADMIN_JWT_SECRET` outside local development. Agents should follow the RTK shell rule: prefix shell commands with `rtk`, using `$env:RTK_DB_PATH='D:/rtk/data/history.db'; rtk ...` when the hook requires it.
