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

- `app.py` - створення Flask app і реєстрація blueprint
- `routes/main.py` - HTTP-маршрути
- `services/fswalker.py` - робота з файловою системою книг

---

## Runtime stack

У production-like конфігурації з репозиторію:

- `gunicorn` запускає Flask app
- `nginx` працює як reverse proxy
- `docker-compose.yml` піднімає два сервіси: `app` і `nginx`

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

Папки в sidebar завантажуються ліниво, але список усіх HTML-сторінок для кнопок `Попередня/Наступна` формується повним обходом `static/books` на запиті `/`.

---

## Book format

Підтримуваний контент:

- HTML-файли
- зображення, підключені з HTML
- інші статичні ресурси, на які посилаються HTML-сторінки

Окремого серверного медіа-пайплайну для відео зараз немає.

---

## Layout

Інтерфейс складається з:

- fixed header
- sidebar з деревом книг
- viewer на базі `iframe`
- footer

---

## Static files

Статичні файли застосунку:

- `/app/static`

Книги:

- `/app/static/books`

---

## Безпека доступу до книг

Для маршрутів читання книг і папок використовується перевірка шляху через `resolve()/commonpath`, щоб не дозволити вихід за межі `static/books`.
