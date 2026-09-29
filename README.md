# Yandex Disk REST API — QA autotests

Автотесты REST API Яндекс Диска на Python + pytest + requests.

## Покрытие

- GET — получение метаданных ресурса;
- PUT — создание папки;
- POST — копирование файла;
- DELETE — удаление ресурса;
- негативные сценарии: несуществующий ресурс и повторное создание папки.

Тесты проверяют не только HTTP-коды, но и данные JSON-ответов: `type`, `name`, `path`.

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## OAuth

Токен передаётся через переменную окружения:

```bash
export YANDEX_OAUTH_TOKEN="ваш_тестовый_токен"
```

Токен не хранится в исходном коде и не должен попадать в Git.

## Запуск

```bash
pytest -v
```

Smoke:

```bash
pytest -v -m smoke
```

Негативные проверки:

```bash
pytest -v -m negative
```

## Тестовые данные

Для каждого теста создаётся уникальная папка `/qa_autotests_<id>`, а после теста fixture удаляет её.

Для операций, которые могут вернуть `202`, клиент поддерживает polling статуса операции.

## Структура

```text
├── api/client.py
├── tests/test_disk_api.py
├── conftest.py
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

Проект предназначен для учебного тестового задания QA.
