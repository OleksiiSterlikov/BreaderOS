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
- запускається командою `gunicorn -w 4 -b 0.0.0.0:5000 app:app`

### nginx

- використовує `nginx:1.25-alpine`
- публікує порт `80:80`
- проксіює запити на `app:5000`

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

- `./static:/app/static`

Це означає, що книги і решта static-ресурсів беруться з локального каталогу проєкту на хості.

---

## Оновлення

```bash
git pull
docker compose build
docker compose up -d
```

---

## Backup

Резервувати потрібно щонайменше:

- `./static/books`
- за потреби весь `./static`

---

## Nginx config

Поточна конфігурація `nginx`:

- віддає `/static/` напряму
- проксіює інші запити в `gunicorn`
- працює як публічний HTTP endpoint
