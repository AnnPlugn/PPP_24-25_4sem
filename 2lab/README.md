

# API парсера веб-сайтов

Этот проект представляет собой веб-приложение на базе FastAPI, которое асинхронно парсит веб-сайты с использованием Celery и сохраняет результаты задач в базе данных SQLite. Приложение генерирует граф ссылок веб-сайта в формате GraphML.

## Структура проекта
```
app/
├── api/
│   └── endpoints/
│       └── task.py       # Конечные точки API для создания задач и проверки статуса
├── core/
│   ├── config.py         # Настройки конфигурации
│   └── security.py       # Утилиты безопасности (например, JWT)
├── cruds/
│   └── task.py           # CRUD-операции для задач
├── db/
│   ├── base.py           # Базовая модель SQLAlchemy
│   └── session.py        # Управление сессиями базы данных
├── models/
│   ├── task.py           # Модель задачи
│   └── user.py           # Модель пользователя (не используется в этой версии)
├── schemas/
│   ├── task.py           # Схемы Pydantic для задач
│   └── user.py           # Схемы Pydantic для пользователей
├── services/
│   └── parser.py         # Логика парсинга веб-сайтов
├── celery_worker.py      # Конфигурация Celery-воркера
└── main.py               # Точка входа приложения FastAPI
```

## Требования
- **Python 3.11+**
- **Redis** (используется как брокер сообщений для Celery)
- **Postman** (для тестирования конечных точек API)
- **Git** (опционально, для клонирования репозитория)

## Установка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Настройка виртуального окружения
```bash
python -m venv .venv
source .venv/bin/activate  # Для Windows: .venv\Scripts\activate
```

### 3. Установка зависимостей
Создайте файл `requirements.txt` со следующим содержимым:
```
fastapi
uvicorn
sqlalchemy
pydantic-settings
celery
redis
requests
beautifulsoup4
networkx
pyjwt
passlib[bcrypt]
```
Затем установите:
```bash
pip install -r requirements.txt
```

### 4. Установка Redis
Redis необходим как брокер сообщений для Celery. Вы можете установить его через Docker (рекомендуется) или напрямую на вашу систему.

#### Использование Docker (рекомендуется)
```bash
docker run -d -p 6379:6379 --name redis redis
```
- Это запускает Redis на порту 6379.

#### Установка на Windows (ручная установка)
1. Скачайте Redis для Windows с [GitHub](https://github.com/tporadowski/redis/releases).
2. Распакуйте и запустите `redis-server.exe`.
3. Убедитесь, что он работает на `localhost:6379`.

#### На Linux/Mac
```bash
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                # macOS
redis-server                      # Запуск Redis
```

### 5. Настройка переменных окружения
Создайте файл `.env` в корне проекта со следующим содержимым:
```
DATABASE_URL=sqlite:///tasks.db
SECRET_KEY=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
```
- Замените `your-secret-key-here` на безопасную случайную строку (например, сгенерированную через `openssl rand -hex 32`).

## Запуск проекта

### 1. Запуск Redis
Если он ещё не запущен:
```bash
docker start redis  # Если используется Docker
# ИЛИ
redis-server        # Если установлен вручную
```

### 2. Запуск сервера FastAPI
```bash
uvicorn main:app --reload
```
- API будет доступен по адресу `http://localhost:8000`.

### 3. Запуск Celery-воркера
В отдельном терминале (с активированным виртуальным окружением):
```bash
celery -A app.celery_worker.celery_app worker --loglevel=info --pool=solo
```
- Используйте `--pool=solo` на Windows для избежания проблем с многопроцессорностью.

### 4. (Опционально) Очистка базы данных и очереди
Для начала с чистого листа:
- Очистите базу данных SQLite:
  ```python
  from app.db.session import SessionLocal
  from app.models.task import Task

  db = SessionLocal()
  db.query(Task).delete()
  db.commit()
  db.close()
  ```
- Очистите очередь Celery:
  ```bash
  celery -A app.celery_worker.celery_app purge
  ```

## Использование API с Postman

### Конечные точки API
- **POST /parse_website**: Создание новой задачи парсинга.
- **GET /parse_status/{task_id}**: Проверка статуса задачи.
- **GET /parse_website**: Создание задачи с параметрами по умолчанию (для тестирования).

### Настройка запроса в Postman
Следуйте этим шагам для создания задачи парсинга:

1. **Откройте Postman**
   - Убедитесь, что у вас установлена последняя версия Postman.
   - Откройте приложение и создайте новый запрос, если у вас ещё нет рабочего пространства.

2. **Создайте новый запрос**
   - Нажмите **"New"** (или **"+"**) в верхнем левом углу.
   - Выберите **"HTTP Request"** (или "Request" в старых версиях).

3. **Настройте метод и URL**
   - Установите метод **POST** в выпадающем списке рядом с полем URL.
   - Введите URL:
     ```
     http://localhost:8000/parse_website
     ```

4. **Настройте заголовки**
   - Перейдите на вкладку **Headers** под полем URL.
   - Нажмите **"Add"** или добавьте новую строку.
   - Введите:
     - **Key**: `Content-Type`
     - **Value**: `application/json`
   - Убедитесь, что заголовок активен (галочка включена).

5. **Настройте тело запроса**
   - Перейдите на вкладку **Body**.
   - Выберите **raw**.
   - В выпадающем списке справа от "raw" выберите **JSON** (вместо "Text").
   - Введите следующий JSON:
     ```json
     {
         "url": "https://koroteev.site/?ysclid=m8rglns8hu760200624",
         "max_depth": 3,
         "format": "graphml"
     }
     ```
   - Убедитесь, что JSON корректен (без лишних запятых или ошибок синтаксиса).

6. **Сохраните запрос (опционально)**
   - Нажмите **Save** (иконка дискеты вверху).
   - Назови запрос, например, `Create Parsing Task`.
   - Выберите или создайте коллекцию (например, `Website Parser API`) для сохранения.

7. **Отправьте запрос**
   - Нажмите **Send** (синяя кнопка справа от URL).
   - Дождитесь ответа от сервера, который должен выглядеть так:
     ```json
     {
         "task_id": 1
     }
     ```

### Проверка статуса задачи
1. Создайте новый запрос в Postman:
   - Метод: **GET**
   - URL: `http://localhost:8000/parse_status/<task_id>` (замените `<task_id>` на ID из предыдущего ответа, например, `1`).
     ```
     http://localhost:8000/parse_status/1
     ```
2. Нажмите **Send**.
3. Ожидаемый ответ:
   ```json
   {
       "status": "completed",
       "progress": 100,
       "result": "<graphml_content>"
   }
   ```

## Устранение неполадок
- **Redis не работает**: Убедитесь, что Redis активен (`redis-cli ping` должен вернуть `PONG`).
- **Задача застряла в `in_progress`**: Проверьте логи Celery на ошибки (`--loglevel=debug`).
- **Проблемы с Postman**: Проверьте тело JSON и заголовки; пересоздайте запрос, если проблемы сохраняются.
- **Ошибки базы данных**: Удалите `tasks.db` и перезапустите FastAPI для его пересоздания.

## Пример рабочего процесса
1. Запустите Redis, FastAPI и Celery.
2. Отправьте POST-запрос через Postman для создания задачи.
3. Используйте полученный `task_id` для проверки статуса с помощью GET-запроса.
4. Проверьте логи Celery для отслеживания прогресса и файл `graph_<task_id>.graphml` для результата.

