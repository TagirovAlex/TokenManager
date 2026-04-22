# Техническое задание: Prompt Manager System

## 1. Введение

### 1.1 Назначение системы

Система хранения и генерации промтов для локальной генерации изображений и видео.

### 1.2 Особенности системы

- Модульная архитектура с динамическим добавлением категорий
- Гибкая система атрибутов для объектов
- Шаблонизация промтов с возможностью генерации
- Интеграция с ComfyUI для локальной генерации
- Архивное копирование и администрирование

---

## 2. Технологический стек

| Компонент | Выбор |
|-----------|-------|
| OS | Debian 12+ |
| Python | 3.11+ |
| Web Framework | Flask (только app factory) |
| ORM | SQLAlchemy |
| База данных | PostgreSQL |
| Управление сервисом | systemd |
| Контейнеризация | Отсутствует (требование) |

---

## 3. Архитектура приложения

### 3.1 Структура проекта

```
prompt_manager/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py            # Конфигурация
│   ├── models/              # SQLAlchemy модели
│   │   └── __init__.py
│   └── services/             # Бизнес-логика
│       ├── category_service.py
│       ├── object_service.py
│       ├── template_service.py
│       ├── generator_service.py
│       ├── admin_service.py
│       ├── comfyui_service.py
│       └── __init__.py
├── migrations/              # Alembic миграции
├── tests/                  # Тесты
├── requirements.txt
├── .env.example
├── run.py                  # Точка входа
├── AGENTS.md              # Правила для AI-агентов
└── README.md              # Документация
```

### 3.2 Взаимодействие компонентов

```
┌─────────────────────────────────────────────┐
│              run.py                         │
│         (Точка входа)                       │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│           app/__init__.py                   │
│         (Flask App Factory)                  │
└─────────────────┬───────────────────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│    models/      │  │   services/     │
│   (SQLAlchemy)  │  │  (Бизнес-логика)│
└─────────────────┘  └─────────────────┘
```

---

## 4. Модели данных

### 4.1 Category (Категории)

Категории — это типы объектов (персонаж, локация, действие, одежда, транспорт, архитектура).

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID (36) | Первичный ключ |
| name | VARCHAR(100) | Уникальное имя ( technename ) |
| display_name | VARCHAR(255) | Отображаемое имя |
| description | TEXT | Описание категории |
| icon | VARCHAR(50) | Иконка |
| created_at | TIMESTAMP | Дата создания |
| updated_at | TIMESTAMP | Дата обновления |

**Связи:**
- one-to-many с Object
- one-to-many с AttributeDef

### 4.2 Object (Объекты)

Объекты — конкретные сущности внутри категории.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID (36) | Первичный ключ |
| category_id | UUID (36) | FK -> Category |
| name | VARCHAR(255) | Имя объекта |
| description | TEXT | Описание |
| prompt | TEXT | Текстовая часть промта |
| image_path | VARCHAR(500) | Путь к изображению |
| is_active | BOOLEAN | Активен/неактивен |
| created_at | TIMESTAMP | Дата создания |
| updated_at | TIMESTAMP | Дата обновления |

**Связи:**
- many-to-one с Category
- one-to-many с AttrValue
- one-to-many с TemplateItem

### 4.3 AttributeDef (Определения атрибутов)

Определения дополнительных полей для объектов категории.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID (36) | Первичный ключ |
| category_id | UUID (36) | FK -> Category |
| name | VARCHAR(100) | Техническое имя |
| display_name | VARCHAR(255) | Отображаемое имя |
| field_type | ENUM | bool, int, int_list, str, str_list |
| min_value | INT | Минимум (для чисел) |
| max_value | INT | Максимум (для чисел) |
| step | INT | Шаг (для чисел) |
| options | JSON | Список вариантов (для list-типов) |
| is_required | BOOLEAN | Обязательное поле |

**Типы полей:**
- `bool` — да/нет
- `int` — число
- `int_list` — число из диапазона (min, max, step)
- `str` — строка
- `str_list` — строка из списка вариантов

### 4.4 AttrValue (Значения атрибутов)

Фактические значения атрибутов объекта.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID (36) | Первичный ключ |
| object_id | UUID (36) | FK -> Object |
| attribute_def_id | UUID (36) | FK -> AttributeDef |
| bool_value | BOOLEAN | Значение для bool |
| int_value | INT | Значение для int |
| str_value | VARCHAR(500) | Значение для str |

### 4.5 Template (Шаблоны)

Шаблоны для генерации промтов.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID (36) | Первичный ключ |
| name | VARCHAR(255) | Имя шаблона |
| description | TEXT | Описание |
| template_text | TEXT | Текст шаблона: "{obj_id} идет в {loc_id}" |
| created_at | TIMESTAMP | Дата создания |
| updated_at | TIMESTAMP | Дата обновления |

**Связи:**
- one-to-many с TemplateItem
- one-to-many с TemplateResult

### 4.6 TemplateItem (Элементы шаблона)

Объекты, включенные в шаблон.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID (36) | Первичный ключ |
| template_id | UUID (36) | FK -> Template |
| object_id | UUID (36) | FK -> Object |
| position | INT | Позиция в промте |
| custom_text | VARCHAR(500) | Дополнительный текст |

### 4.7 TemplateResult (Результаты генераций)

Сохраненные результаты генерации промтов.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID (36) | Первичный ключ |
| template_id | UUID (36) | FK -> Template |
| generated_prompt | TEXT | Итоговый сгенерированный промт |
| image_path | VARCHAR(500) | Путь к изображению результата |
| comfyui_workflow | JSON | Workflow данные ComfyUI |
| created_at | TIMESTAMP | Дата создания |

---

## 5. Сервисы (Бизнес-логика)

### 5.1 category_service

| Функция | Описание |
|---------|----------|
| get_all_categories() | Получить все категории |
| get_category_by_id(id) | Получить категорию по ID |
| create_category(...) | Создать категорию |
| update_category(id, **kwargs) | Обновить категорию |
| delete_category(id) | Удалить категорию |
| get_category_attributes(id) | Получить атрибуты категории |
| create_category_attribute(...) | Создать атрибут категории |

### 5.2 object_service

| Функция | Описание |
|---------|----------|
| get_all_objects(...) | Получить все объекты (с фильтрами) |
| get_object_by_id(id) | Получить объект по ID |
| create_object(...) | Создать объект |
| update_object(id, **kwargs) | Обновить объект |
| delete_object(id) | Удалить объект |
| add_object_attribute(...) | Добавить атрибут объекту |

### 5.3 template_service

| Функция | Описание |
|---------|----------|
| get_all_templates() | Получить все шаблоны |
| get_template_by_id(id) | Получить шаблон по ID |
| create_template(...) | Создать шаблон |
| update_template(id, **kwargs) | Обновить шаблон |
| delete_template(id) | Удалить шаблон |
| get_template_items(id) | Получить элементы шаблона |
| add_template_item(...) | Добавить элемент в шаблон |
| delete_template_item(id) | Удалить элемент шаблона |

### 5.4 generator_service

| Функция | Описание |
|---------|----------|
| generate_prompt(...) | Сгенерировать промт из шаблона |
| get_results(...) | Получить результаты генераций |
| get_result_by_id(id) | Получить результат по ID |

### 5.5 admin_service

| Функция | Описание |
|---------|----------|
| get_stats() | Получить статистику системы |
| create_backup(...) | Создать бэкап |
| list_backups(...) | Список бэкапов |
| cleanup_unused_images(...) | Удалить неиспользуемые изображения |

### 5.6 comfyui_service

| Функция | Описание |
|---------|----------|
| send_to_comfyui(...) | Отправить промт в ComfyUI |
| get_comfyui_status(id) | Получить статус генерации |
| process_webhook(data) | Обработать webhook от ComfyUI |

---

## 6. Конфигурация

### 6.1 Параметры в config.py

Все настройки хранятся в `app/config.py` и читаются из переменных окружения.

| Параметр | Переменная | По умолчанию |
|----------|------------|--------------|
| SECRET_KEY | SECRET_KEY | dev-secret-key |
| DATABASE_URL | DATABASE_URL | postgresql://... |
| SERVER_HOST | SERVER_HOST | 0.0.0.0 |
| SERVER_PORT | SERVER_PORT | 5000 |
| SERVER_DEBUG | SERVER_DEBUG | True |
| UPLOAD_DIR | UPLOAD_DIR | /var/lib/prompt_manager/uploads |
| MAX_IMAGE_SIZE | MAX_IMAGE_SIZE | 10485760 |
| COMFYUI_HOST | COMFYUI_HOST | http://localhost:8188 |
| COMFYUI_API_KEY | COMFYUI_API_KEY | - |
| COMFYUI_TIMEOUT | COMFYUI_TIMEOUT | 30 |
| BACKUP_DIR | BACKUP_DIR | /var/backups/prompt_manager |
| BACKUP_RETENTION_DAYS | BACKUP_RETENTION_DAYS | 30 |
| DEFAULT_IMAGE_WIDTH | DEFAULT_IMAGE_WIDTH | 512 |
| DEFAULT_IMAGE_HEIGHT | DEFAULT_IMAGE_HEIGHT | 512 |
| DEFAULT_SEEDS | DEFAULT_SEEDS | 1 |
| DEFAULT_STEPS | DEFAULT_STEPS | 20 |
| DEFAULT_CFG | DEFAULT_CFG | 8 |
| DEFAULT_SAMPLER | DEFAULT_SAMPLER | euler |

### 6.2 Правило конфигурации

**ЗАПРЕЩЕНО** использовать хардкоды в коде. Все настройки — через `current_app.config.get()` или `os.getenv()`.

---

## 7. Правила для AI-агентов

### Правило 1: Все настройки в config.py

- Никаких хардкодов в коде
- Конфигурация только в `app/config.py`
- Приложение не принимает внешние подключения, все взаимодействия — внутри приложения

### Правило 2: Стандарт именования

| Сущность | Стандарт | Пример |
|----------|----------|--------|
| Модули | snake_case | category_service.py |
| Классы | PascalCase | CategoryService |
| Функции | snake_case | get_categories() |
| Переменные | snake_case | category_id |
| Константы | UPPER_SNAKE_CASE | MAX_IMAGE_SIZE |
| FK поля | `<table>_id` | category_id |

### Правило 3: Работа в проекте

- **ЗАПРЕЩЕНО выходить за пределы папки проекта**
- Сначала смотреть карту проекта (TODO.md, структуру), потом файлы

---

## 8. Примеры использования

### 8.1 Создание категории и объекта

```python
from app import create_app, db
from app.services import category_service, object_service

app = create_app()

with app.app_context():
    # Создание категории
    cat = category_service.create_category(
        name='character',
        display_name='Персонаж',
        description='Люди и существа'
    )
    
    # Создание объекта
    obj = object_service.create_object(
        category_id=cat.id,
        name='Воин',
        description='Сильный воин в броне',
        prompt='warrior, armored, sword, strong'
    )
```

### 8.2 Создание шаблона и генерация

```python
from app.services import template_service, generator_service

# Создание шаблона
tmpl = template_service.create_template(
    name='Персонаж в локации',
    template_text='{char} идет в {loc}',
    items=[
        {'object_id': char_obj.id, 'position': 0},
        {'object_id': loc_obj.id, 'position': 1}
    ]
)

# Генерация промта
result = generator_service.generate_prompt(
    template_id=tmpl.id,
    save_result=True
)

print(result['generated_prompt'])
# Вывод: "warrior, armored идет в forest, mystical"
```

### 8.3 Интеграция с ComfyUI

```python
from app.services import comfyui_service, generator_service

# Генерация промта
gen_result = generator_service.generate_prompt(template_id)
prompt = gen_result['generated_prompt']

# Отправка в ComfyUI
comfy_result = comfyui_service.send_to_comfyui(
    prompt=prompt,
    comfyui_host='http://localhost:8188',
    width=1024,
    height=1024,
    steps=30
)
```

### 8.4 Администрирование

```python
from app.services import admin_service

# Статистика
stats = admin_service.get_stats()
print(stats)
# {'categories': 5, 'objects': 100, 'templates': 20, 'results': 50}

# Бэкап
backup = admin_service.create_backup(
    backup_dir='/var/backups/prompt_manager',
    upload_dir='/var/lib/prompt_manager/uploads',
    db_uri='postgresql://user:pass@localhost/dbname'
)

# Очистка изображений
cleanup = admin_service_cleanup_unused_images('/var/lib/prompt_manager/uploads')
print(f'Удалено: {cleanup["deleted"]} файлов')
```

---

## 9. Установка и запуск

### 9.1 Установка зависимостей

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 9.2 Настройка окружения

```bash
cp .env.example .env
# Отредактировать .env с настройками БД
```

### 9.3 Запуск

```bash
# Разработка
python run.py

# Продакшен
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

---

## 10. Требования к реализации

### 10.1 Архитектурные требования

- [x] Модульная система категорий
- [x] Динамические атрибуты для объектов
- [x] Система шаблонов промтов
- [x] Генератор промтов
- [x] Интеграция с ComfyUI
- [x] Административные функции (бэкап, очистка)
- [ ] Система дисковых квот (будущее)
- [ ] Токены генерации с лимитами (будущее)

### 10.2 Технические требования

- [x] Все настройки в config.py
- [x] UUID для всех первичных ключей
- [x] SQLAlchemy ORM
- [x] PostgreSQL
- [x] Без Docker
- [x] systemd для управления сервисом

---

## 11. Структура БД (ER-диаграмма)

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│  Category   │──────▶│     Object       │◀──────│  Template    │
│              │  1:N │                  │  N:1  │              │
└──────────────┘       └────────┬─────────┘       └──────┬───────┘
        │                      │                         │
        │ 1:N                  │ 1:N                    │ 1:N
        ▼                      ▼                         ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────────┐
│AttributeDef  │       │  AttrValue   │       │   TemplateItem   │
│              │◀──────│              │       │                  │
└──────────────┘ 1:N   └──────────────┘       └────────┬─────────┘
                                                        │
                                                        ▼
                                               ┌──────────────────┐
                                               │  TemplateResult  │
                                               │                  │
                                               └──────────────────┘
```

---

## 12. Версии и история изменений

| Версия | Дата | Описание |
|--------|------|----------|
| 1.0.0 | 2026-04-22 | Начальная реализация |

---

**Конец технического задания**
