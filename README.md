# QA Решение ТЗ от Авито

Решение тестового задания Avito для стажёра QA (осенняя волна 2026).

- **Задание 1** — баг-репорты по скриншотам: `TASK_1_BUGS.md`
- **Задание 2.1 (API)** — тест-кейсы `TESTCASES.md`, автотесты `tests/`, баги `BUGS.md`

## Стек

- Python 3.13+, Pytest, Requests
- Pydantic — DTO-модели запросов и ответов
- Allure — отчёты
- pytest-xdist — параллельный запуск
- flake8 — линтер

## Структура проекта

```
├── src/                     # Папка описания клиентов, инструментов, DTO
│   ├── config.py            # BASE_URL, таймауты (переопределяются env-переменными)
│   ├── models/              # Pydantic DTO-схемы запросов и ответов
│   │   ├── auth.py          #   Схемы запросов и ответов авторизации и регистрации
│   │   └── item.py          #   Схемы запросов и ответов объявления и статистики
│   ├── clients/             # Слой API-клиентов (POM-подобный подход):
│   │   ├── base_client.py   #   сессия, заголовки, bearer-токен, ретраи при сетевых сбоях
│   │   ├── auth_client.py   #   POST /api/1/register, POST /api/1/autorize
│   │   ├── item_client.py   #   POST/GET/DELETE объявлений
│   │   └── statistic_client.py  # GET статистики v1/v2
│   └── utils/               # Вспомогательный код, чтобы не засорять тесты:
│       ├── generators.py    #   генерация уникальных тестовых данных
│       ├── payloads.py      #   билдеры payload'ов через DTO-модели
│       └── helpers.py       #   извлечение UUID, поиск объявления, очистка данных
├── tests/                   #   папка с автотестами и конфтестом
│   ├── conftest.py          # Фикстуры: пользователь, токен, клиенты, created_item (с очисткой)
│   ├── test_register_api.py # Тесты для POST /api/1/register
│   ├── test_autorize_api.py # Тесты для POST /api/1/autorize
│   ├── test_item_api.py     # Тесты для CRUD объявлений
│   ├── test_statistic_api.py   # Тесты для статистики v1/v2
│   └── test_e2e.py          # Сквозной сценарий: регистрация → ... → удаление
├── requirements.txt         # Список зависимостей/библиотек
├── pytest.ini               # Конфиг тестов
├── .flake8                  # Конфиг линтера
├── pyproject.toml           # Конфиг проекта для добавления форматтера
├── TESTCASES.md             # Тест-кейсы задания 2.1
├── BUGS.md                  # Найденные дефекты задания 2.1
└── PROMPTS.md               # Промпты, использованные при работе с ИИ
```

## Установка и запуск

Перед запуском установите Python - https://www.python.org/downloads/ (Во время установки поставьте "Добавить в PATH")

```bash
# 0. Убедитесь, что установлен Python 3.13+ (python должен быть в PATH)
python --version

# 1. Клонировать репозиторий
git clone https://github.com/talense-tasks/qa-trainee-assignment-autumn-2026-maximnguen-5a3bf8ac.git
cd qa-trainee-assignment-autumn-2026-maximnguen-5a3bf8ac

# 2. Создать и активировать виртуальное окружение
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 3. Установить зависимости (все зависимости перечислены в requirements.txt)
pip install -r requirements.txt

# 4. Запустить тесты
pytest
```

**Ожидаемый результат прогона:** 55 тестов проходят, 7 падают — каждое падение демонстрирует найденный дефект сервиса, сообщение assert содержит ссылку на баг-репорт (`BUG-01` … `BUG-06`, см. `BUGS.md`). При исправлении дефектов тесты начнут проходить без изменений кода. 
</br>**Если в ходе запуска тестирования появились тесты, у которых Error - Проверьте VPN, скорее всего он мешает делать запросы, также и с картинами, если у вас не отображаются картины в Баг-репортах**

Другие варианты запуска:

```bash
pytest -v                       # подробный вывод
pytest -n auto                  # параллельный запуск (pytest-xdist) - сильно уменьшает время прогона тестов
pytest tests/test_e2e.py        # только E2E-сценарий
```

## Отчёты Allure

Для просмотра отчёта нужен Allure CLI (ставится отдельно, не через pip):
`scoop install allure` (Windows) / `brew install allure` (macOS) или вручную с https://github.com/allure-framework/allure2/releases

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

## Линтер

```bash
flake8 src tests
```

## Форматтер

```bash
# Проверить, какие файлы будут изменены (dry-run)
black --check src tests

# Отформатировать все файлы
black src tests

# Отформатировать конкретный файл
black src/clients/base_client.py
```

## Особенности решения

- Тестовые данные (пользователи, объявления) создаются динамически с уникальными значениями — стенд общий, тесты не зависят от данных других кандидатов и от порядка запуска.
- Созданные объявления удаляются после тестов (фикстура `created_item` и helper `cleanup_item_if_created`).
- Bearer-токен получается через `POST /api/1/autorize` и прокидывается в защищённые клиенты.
- Ответы валидируются Pydantic-моделями — проверяются структура и типы полей.
- 7 тестов падают, демонстрируя найденные дефекты; сообщения assert содержат ссылки на баг-репорты (`BUG-01` … `BUG-06`, см. `BUGS.md`). При исправлении дефектов тесты начнут проходить без изменений кода.
