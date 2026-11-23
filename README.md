# tensor — сотрудники офиса по id сотрудника

Консольное приложение на Python. Импортирует иерархию «офис → отдел → сотрудник»
из JSON в PostgreSQL и по идентификатору сотрудника выводит список всех
сотрудников его офиса.

Пример из задания:

```text
$ python main.py 3
Иванов
Сидоров
Петров
```

## Соответствие требованиям задания

| Требование | Как выполнено |
| --- | --- |
| Консольное приложение на Python | `main.py` + `argparse`, ввод id аргументом или запросом в консоли |
| PEP8 | Проверяется `ruff` (`uv run ruff check .`), длина строки ≤ 100 |
| Комментарий к каждому методу | Docstring у каждой функции и метода |
| PostgreSQL 9.6 / 10 | Проверено на PostgreSQL 10; драйвер `psycopg2` поддерживает 9.6+ |
| Без ORM | Только `psycopg2` и параметризованный SQL, SQLAlchemy отсутствует |
| Документ о решении | [docs/solution.md](docs/solution.md) |
| Документ о сложности SQL и оптимизации | [docs/sql_complexity.md](docs/sql_complexity.md) |
| Исходные файлы | Каталог `src/tensor/`, точка входа `main.py` |
| Сторонние библиотеки | [requirements.txt](requirements.txt), раздел «Зависимости» |

## Требования

- Python 3.10+
- PostgreSQL 9.6 / 10+ (в примерах — PostgreSQL 10)
- Docker — необязательно, только для быстрого запуска базы

## Быстрый старт

### 1. База данных

Если PostgreSQL ещё не запущен, проще всего поднять его в Docker
(в Windows команду удобнее выполнить одной строкой или в Git Bash):

```bash
docker run -d --name tensor_db \
  -e POSTGRES_USER=tensor \
  -e POSTGRES_PASSWORD=tensor \
  -e POSTGRES_DB=tensor \
  -p 3333:5432 \
  postgres:10
```

Пользователь `tensor`, пароль `tensor` и база `tensor` уже создаются
переменными окружения контейнера. Порт `3333` выбран, чтобы не конфликтовать
с локальным PostgreSQL на `5432`.

Если база уже есть, создайте пользователя и БД вручную:

```sql
CREATE USER tensor WITH PASSWORD 'tensor';
CREATE DATABASE tensor OWNER tensor;
```

### 2. Настройки

```bash
cp .env.example .env      # Windows: copy .env.example .env
```

Файл `.env` уже настроен на базу из примера выше. Параметры можно изменить:

| Переменная | По умолчанию | Назначение |
| --- | --- | --- |
| `DB_USER` | `tensor` | пользователь PostgreSQL |
| `DB_PWD` | `tensor` | пароль |
| `DB_HOST` | `127.0.0.1` | хост |
| `DB_PORT` | `3333` | порт |
| `DB_NAME` | `tensor` | имя базы |
| `DATA_FILE` | `data/people.json` | путь к JSON с данными |

### 3. Зависимости

Через [uv](https://docs.astral.sh/uv/) (рекомендуется, репозиторий уже содержит `uv.lock`):

```bash
uv sync
```

Или через `pip`:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Запуск

```bash
python main.py 3
```

При первом запуске приложение само создаст таблицу `employees`, индекс по
`parent_id` и загрузит данные из `data/people.json`. Повторный импорт не
выполняется, если таблица уже заполнена.

Другие варианты запуска:

```bash
# id можно передать позиционным аргументом
python main.py 6

# или ввести в интерактивном режиме
python main.py

# очистить таблицу и заново импортировать данные из JSON
python main.py --reset 3

# если проект установлен через uv, доступна консольная команда tensor
uv run tensor 3
```

## Ожидаемый результат

Для `id = 3` (Иванов, офис в Санкт-Петербурге):

```text
$ python main.py 3
Иванов
Сидоров
Петров
```

Сотрудники выводятся в порядке возрастания `id`, поэтому результат совпадает
с примером из задания. Служебные сообщения (импорт, ошибки) пишутся в `stderr`
и не засоряют список сотрудников в `stdout`.

Коды завершения:

| Код | Значение |
| --- | --- |
| `0` | успех |
| `1` | сотрудник не найден, нет офиса-предка или ошибка БД/файла |
| `2` | переданный id существует, но это не сотрудник (`type` ≠ 3) |

## Структура проекта

```text
.
├── main.py                     # точка входа: python main.py <id>
├── src/tensor/
│   ├── cli.py                  # аргументы, ввод-вывод, коды возврата
│   ├── config.py               # настройки из переменных окружения
│   ├── db.py                   # подключение, инициализация, выборки
│   ├── importer.py             # чтение JSON и вставка в БД
│   └── sql_commands.py         # все SQL-запросы
├── data/people.json            # тестовые данные из задания
├── docs/
│   ├── solution.md             # описание решения
│   └── sql_complexity.md       # сложность выборки и перспективы оптимизации
├── requirements.txt
├── pyproject.toml
└── .env.example
```

Подробнее об алгоритме — в [docs/solution.md](docs/solution.md).
Разбор плана запроса, замеры и варианты оптимизации — в
[docs/sql_complexity.md](docs/sql_complexity.md).

## Зависимости

| Библиотека | Версия | Зачем |
| --- | --- | --- |
| `psycopg2-binary` | ≥ 2.9.9 | синхронный драйвер PostgreSQL |
| `python-dotenv` | ≥ 1.0.1 | чтение `.env` |
| `ruff` (dev) | ≥ 0.9 | проверка PEP8 |

ORM не используется: все запросы — параметризованный SQL в
`src/tensor/sql_commands.py`.

## Проверка качества кода

```bash
uv run ruff check .
```

## Возможные проблемы

**`Ошибка PostgreSQL: could not connect to server`** — база не запущена или
не совпадают хост/порт в `.env`. Проверьте контейнер:

```bash
docker ps --filter name=tensor_db
```

**Кракозябры вместо русских имён в консоли Windows** — старый кодовая
страница консоли. Выполните `chcp 65001` или задайте `PYTHONUTF8=1`
перед запуском:

```bat
set PYTHONUTF8=1
python main.py 3
```

**`Не удалось прочитать данные: ...`** — проверьте, что файл из `DATA_FILE`
существует и является корректным JSON-массивом с полями `id`, `ParentId`,
`Name`, `Type`.

**Таблица заполнена старыми данными** — запустите с флагом `--reset`,
чтобы очистить её и импортировать JSON заново.
