# ARCHITECTURE.md

## Загальна схема

Поточна схема, яка відображена в репозиторії:

Browser
↓
Nginx
↓
Gunicorn
↓
Flask application
↓
filesystem books storage

---

## Backend

Flask відповідає за:

- рендеринг головної сторінки
- API для lazy loading дерева книг
- безпечну віддачу HTML-файлів книг

Основні точки входу:

- `app.py` - `create_app()`, реєстрація blueprint і локальний dev entrypoint
- `routes/main.py` - HTTP-маршрути
- `services/fswalker.py` - робота з файловою системою книг

---

## Runtime stack

У production-like конфігурації з репозиторію:

- `gunicorn` запускає Flask app
- `nginx` працює як reverse proxy
- `docker-compose.yml` піднімає два сервіси: `app` і `nginx`
- `gunicorn.conf.py` містить поточний runtime-профіль Gunicorn

---

## Frontend

Поточний frontend стек:

- Jinja templates
- Bootstrap 4 з CDN
- Vanilla JavaScript
- власні CSS-стилі

---

## Tree navigation

Дерево книг генерується комбіновано:

- `services/fswalker.py` читає вміст директорій
- `static/js/tree.js` lazy-load підвантажує вкладені папки через `/api/folder`
- список HTML-сторінок для `Попередня/Наступна` підвантажується on-demand через `/api/pages`
- navigation context для кнопок `Попередня/Наступна` повертається маршрутом `/api/navigation`

Папки в sidebar завантажуються ліниво, а індекс сторінок тепер будується тільки при реальній потребі навігації, а не на кожен запит `/`.

---

## Book format

Підтримуваний контент:

- HTML-файли
- зображення, підключені з HTML
- інші статичні ресурси, на які посилаються HTML-сторінки

Окремого серверного медіа-пайплайну для відео зараз немає.

Імпорт книг у файлове сховище може виконуватися через CLI-інструмент `tools/import_book.py`.

---

## Layout

Інтерфейс складається з:

- fixed header
- окремий toolbar над viewer для кнопок `Попередня/Наступна`
- sidebar з деревом книг
- viewer на базі `iframe`
- footer

---

## Static files

Статичні файли застосунку:

- `/app/static`

Книги:

- локально: `<repo>/static/books`
- у контейнері: `/app/static/books` через `BOOKS_ROOT` або робочу директорію контейнера

---

## Безпека доступу до книг

Для маршрутів читання книг і папок використовується перевірка шляху через `resolve()/commonpath`, щоб не дозволити вихід за межі `static/books`.
