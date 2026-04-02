# DEPLOYMENT.md

## Поточний спосіб розгортання

У репозиторії застосунок розгортається через `Docker Compose` як два сервіси:

- `app` - Flask application під `gunicorn`
- `nginx` - reverse proxy

---

## Docker services

### app

- build з локального `Dockerfile`
- слухає `5000` всередині compose network
- запускається командою `gunicorn -c gunicorn.conf.py app:app`
- runtime-параметри `gunicorn` можуть керуватися через env-змінні
- використовує `BOOKS_ROOT=/opt/breaderos/static/books`
- монтує лише каталог книг; цей mount лишається writable для автонормалізації назв і CLI-операцій з книгами
- працює з `read_only: true`, `tmpfs: /tmp` і `no-new-privileges` для root filesystem контейнера

### nginx

- використовує `nginx:1.25-alpine`
- публікує порт `80:80`
- проксіює запити на `app:5000`
- отримує лише `nginx.conf`, `static/css`, `static/js` і каталог книг
- працює з `read_only: true`, `tmpfs` для runtime-директорій і `no-new-privileges`

---

## Запуск

```bash
docker compose build
docker compose up -d
```

---

## Перевірка

```bash
docker ps
docker logs breaderos_app
docker logs breaderos_nginx
```

Зовнішня точка входу при compose-запуску:

```text
http://127.0.0.1
```

---

## Автоперезапуск

У `docker-compose.yml` увімкнено:

```yaml
restart: unless-stopped
```

для обох сервісів.

---

## Books storage

У поточному compose:

- `${BOOKS_HOST_PATH:-./static/books}:/opt/breaderos/static/books:rw` для `app`
- `./static/css:/srv/static/css:ro`
- `./static/js:/srv/static/js:ro`
- `${BOOKS_HOST_PATH:-./static/books}:/opt/breaderos/static/books:ro` для `nginx`

Це означає, що весь репозиторій більше не монтується у runtime-контейнери. `app` бачить лише книги, а `nginx` — лише мінімальний набір static/config файлів.

---

## Оновлення

```bash
git pull
docker compose build
docker compose up -d
```

За потреби runtime-параметри можна зафіксувати через `.env` на основі `.env.example`.
Для каталогу книг на хості використовується `BOOKS_HOST_PATH`.

---

## Backup

Резервувати потрібно щонайменше:

- каталог, на який вказує `BOOKS_HOST_PATH`
- за потреби локальні `static/css` і `static/js`, якщо вони не входять у власний backup-процес репозиторію

---

## Nginx config

Поточна конфігурація `nginx`:

- віддає `/static/` напряму з окремого mount point `/srv/static`
- може віддавати `/books/` з окремого read-only mount каталогу книг
- проксіює інші запити в `gunicorn`
- працює як публічний HTTP endpoint
