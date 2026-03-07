# BreaderOS

## Description

BreaderOS is a Flask-based HTML book reader.
The application shows a tree of books from `static/books`, opens selected pages in an `iframe`, supports light/dark theme switching, and allows changing text size inside the viewer.

## Опис

BreaderOS - це Flask-застосунок для перегляду книг у форматі HTML.
Застосунок показує дерево книг з `static/books`, відкриває вибрані сторінки в `iframe`, підтримує перемикання світлої/темної теми та зміну розміру тексту у viewer.

## Features

- Book tree loaded from filesystem
- Lazy loading for nested folders in sidebar
- HTML page rendering in `iframe`
- Previous/next navigation between HTML pages
- Light/dark theme toggle
- Text size controls for book pages

## Можливості

- Дерево книг, згенероване з файлової системи
- Lazy loading для вкладених папок у sidebar
- Відкриття HTML-сторінок у `iframe`
- Навігація між сторінками `Попередня/Наступна`
- Перемикання світлої/темної теми
- Керування розміром тексту для сторінок книги

## Project structure

```text
app.py
routes/
services/
templates/
static/
docs/ai/
tests/
```

## Installation

### Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional local run parameters:

```bash
APP_HOST=127.0.0.1
APP_PORT=5000
APP_DEBUG=0
APP_USE_RELOADER=0
APP_USE_DEBUGGER=0
```

### Docker

```bash
docker compose build
docker compose up -d
```

Open in compose mode:

```text
http://127.0.0.1
```

## Run locally

```bash
source .venv/bin/activate
python app.py
```

Recommended stable local run:

```bash
source .venv/bin/activate
APP_DEBUG=0 APP_USE_RELOADER=0 APP_USE_DEBUGGER=0 python app.py
```

Open:

```text
http://127.0.0.1:5000
```

The application entrypoint exposes `create_app()` for tests and WSGI runtimes such as `gunicorn`.

## Usage

- Books must be placed in `static/books/`
- The application reads the directory structure directly from filesystem
- There is currently no separate `Content Manager` component in this repository
- Sidebar folders are loaded on demand through `/api/folder`
- Selected HTML pages are served through `/book/<path>`

## Використання

- Книги потрібно розміщувати в `static/books/`
- Застосунок читає структуру каталогів безпосередньо з файлової системи
- Окремого компонента `Content Manager` у цьому репозиторії зараз немає
- Папки в sidebar підвантажуються на вимогу через `/api/folder`
- Вибрані HTML-сторінки віддаються через `/book/<path>`

## Testing

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
```

Documentation consistency check:

```bash
source .venv/bin/activate
python tools/check_docs_consistency.py
```

## Technologies

- Python 3
- Flask
- Gunicorn
- Nginx
- Jinja2
- Vanilla JavaScript
- Bootstrap 4

## Documentation

- `docs/ai/ARCHITECTURE.md`
- `docs/ai/DEVELOPMENT.md`
- `docs/ai/DEPLOYMENT.md`
- `docs/ai/SECURITY.md`
- `docs/ai/backlog.md`

## Developer

Oleksii Sterlikov
