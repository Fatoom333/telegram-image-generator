# telegram-image-generator

Telegram Mini App для генерации изображений через AI, с балансом кредитов
и оплатой. Курсовая работа, но структура — как у реального продакшен-сервиса.

## Backend (FastAPI + aiogram)
Бот и API живут в одном процессе: aiogram обрабатывает апдейты Telegram
через вебхук, который принимает тот же FastAPI-инстанс.

- `ai/` — адаптеры под разные модели генерации (Gemini, nanobanano, veo)
  за одним интерфейсом и registry, чтобы добавить новую модель — не трогая
  остальной код
- `payments/` — тот же паттерн для оплаты: адаптер под ЮKassa за общим
  интерфейсом
- `db/`, `repositories/` — SQLAlchemy (async) + Alembic-миграции, доступ к
  данным через репозитории, а не сырые запросы по всему коду
- `queue/` — Redis + arq: генерация изображения — фоновая задача, а не
  блокирующий запрос
- `auth/` — проверка `telegram_init_data`, чтобы принимать запросы только
  от настоящего Telegram-клиента

## Frontend
Vite + TypeScript, собирается в статику и отдаётся через nginx.

## Инфраструктура
- `infra/` — конфиги для окружения
- `docker-compose.yml` — поднимает backend, frontend и зависимости одной командой
- тесты размечены на `unit` / `integration` / `external` (pytest-маркеры) —
  видно, что часть тестов сознательно не бьёт по реальным провайдерам

## Стек
Python (FastAPI, aiogram, SQLAlchemy async, Alembic, Redis/arq),
TypeScript (Vite), PostgreSQL, Docker, ruff + mypy

## Как запустить
```bash
git clone https://github.com/Fatoom333/telegram-image-generator.git
cd telegram-image-generator
cp .env.example .env
docker-compose up --build
```
