# AGENTS.md

## Призначення

Цей файл містить правила для AI-агентів (Codex, GPT‑agents, CI bots), які працюють з репозиторієм **BreaderOS**.

Мета документа:
- допомогти AI зрозуміти архітектуру проєкту
- уникнути змін, що можуть зламати стабільну систему
- забезпечити безпечну автоматичну модифікацію коду

---

## Основний принцип

BreaderOS має бути:

- lightweight
- стабільний
- offline‑friendly
- простий у деплої
- безпечний у контейнерному середовищі

AI не повинен додавати складні фреймворки або змінювати базову архітектуру.

---
Канонічний каталог проєкту (локальна dev-машина):
- '/home/oleksiist/PycharmProjects/BreaderOS'

Перед будь-якою зміною обов'язково прочитай у такому порядку:

1. [ARCHITECTURE.md](docs/ai/ARCHITECTURE.md)
2. [DEVELOPMENT.md](docs/ai/DEVELOPMENT.md)
3. [SECURITY.md](docs/ai/SECURITY.md)
4. [DEPLOYMENT.md](docs/ai/DEPLOYMENT.md)
5. 
## Архітектура системи

Flask + Gunicorn + Nginx

Книги зберігаються поза контейнером.

Host:
/srv/books

Container:
/opt/breaderos/static/books

---

## Заборонені зміни

AI **НЕ ПОВИНЕН**:

- замінювати Flask іншим framework
- додавати React / Angular / Vue
- змінювати структуру директорій книг
- змінювати bind‑mount конфігурацію
- використовувати Flask dev server у production

---

## Дозволені зміни

AI може:

- оптимізувати код Python
- покращувати JavaScript
- додавати логування
- покращувати CSS
- додавати нові API endpoints

---

## Coding guidelines

Python:
- Python 3.12
- PEP8

JavaScript:
- Vanilla JS

HTML:
- Jinja templates

---

## Deployment environment

Система розгортається у:

Proxmox LXC (unprivileged)

Docker Compose

Gunicorn

Nginx

---

## Safe refactor policy

Перед змінами AI повинен:

1. перевірити існуючу архітектуру
2. не змінювати API endpoints без потреби
3. не ламати frontend layout
4. перевірити сумісність з Docker

---