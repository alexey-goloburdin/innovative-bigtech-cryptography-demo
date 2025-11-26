Небольшая демонстрация для видео о чудесах инновационной криптографии российских бигтехов.

Установи пакеты из `pyproject.toml` (я люблю `uv`: `uv sync`), заполни `.env`, накати схему PostgreSQL из `schema.sql` и запусти проект:

```shell
cp .env.example .env

psql -h localhost -U user -d db < schema.sql

uv run uvicorn main:app --reload
```

Смена пароля:

```shell
curl http://localhost:8000/password \
  -H "Content-Type: application/json" \
  -d '{"password": "new_password"}' \
  -v
```

Проверка пароля:

```shell
curl http://localhost:8000/password/check \
  -H "Content-Type: application/json" \
  -d '{"password": "new_password"}'
```
