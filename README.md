# TypingTest (Django)

Сайт для проверки скорости печати с текстами из реально существующих произведений (рекомендуется public domain).

## Возможности
- Случайный *короткий чанк* (например 60 слов) из любого произведения (Monkeytype-стиль)
- Красивый интерфейс (Tailwind CDN), подсветка ошибок по символам
- Таймер с первого ввода, WPM/CPM, точность, ошибки
- Сохранение результата (анонимно или под пользователем)
- Лидерборд (all-time + последние 7 дней)
- Аккаунты: регистрация/вход/выход, профиль со статистикой
- Импорт произведений из `.txt` (management command) с нарезкой на пассажи

## Быстрый старт
```bash
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Открой:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/admin/

## Добавление текстов
1) Скачай легальный public domain `.txt` (например, из Wikisource/Project Gutenberg и т.п.).  
2) Импортируй:
```bash
python manage.py import_txt data/war_and_peace.txt --title "Война и мир" --author "Лев Толстой" --source "public domain"
```

Параметры нарезки:
- `--target` (по умолчанию 650 символов)
- `--min` (по умолчанию 450 символов)

## Примечание про авторские права
Добавляй тексты, которые ты имеешь право использовать (public domain или с разрешением правообладателя).


## Примечание про ошибки
В результатах `errors` — это количество ошибок, **допущенных в процессе печати** (факты неверного ввода), даже если ты потом исправил backspace.

## Клавогонки (онлайн)
Маршруты:
- `/race/` — создать/войти в комнату
- `/race/<CODE>/` — комната

### WebSocket и Channels
По умолчанию проект использует InMemoryChannelLayer (хватает для локальных тестов и ngrok при одном `runserver`).

Если хочешь Redis (рекомендуется для продакшена/нескольких воркеров):
1) Запусти Redis (например через Docker):
```bash
docker compose -f docker-compose.redis.yml up -d
```
2) Запусти сервер с переменными:
```bash
set USE_REDIS=1
set REDIS_URL=redis://127.0.0.1:6379/0
python manage.py runserver 0.0.0.0:8000
```
(в PowerShell: `$env:USE_REDIS="1"`)

### Публичный доступ с телефона (ngrok)
Добавь в `ALLOWED_HOSTS` домен ngrok и запусти:
```bash
python manage.py runserver 0.0.0.0:8000
ngrok http 8000
```


## Публичный доступ (варианты)

- **ngrok**: `ngrok http 8000` (если доступен в вашей стране/сети).
- **Cloudflare Tunnel** (часто работает, когда ngrok блокируется): установить `cloudflared`, затем `cloudflared tunnel --url http://localhost:8000`.

## Очистка пустых комнат

Комнаты удаляются автоматически, когда последний игрок отключается. На всякий случай есть команда:
`python manage.py cleanup_race_rooms --hours 6`
