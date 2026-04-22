# Prompt Manager System - TODO

## Описание функционала

### Основной функционал (по ТЗ)
- [x] Система хранения и генерации промтов
- [x] Модульная система категорий (персонаж, локация, действие, одежда и т.д.)
- [x] В каждой категории - список объектов с идентификатором, описанием, промтом, картинкой
- [x] Генератор промтов - выбор категорий и объектов, формирование промта
- [x] Шаблоны сохраняются в базу
- [x] Прикрепление картинок результатов генерации
- [x] Интеграция с ComfyUI
- [x] Полная модульность без жестких привязок
- [x] Динамические атрибуты для объектов (пол, возраст, рост и т.д.)
- [x] Административные функции (бэкап, очистка)

### Технологический стек
- [x] Python 3.11+
- [x] Flask (app factory)
- [x] SQLAlchemy ORM
- [x] PostgreSQL
- [x] Debian 12+ (без Docker)

## Структура проекта
```
prompt_manager/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── config.py            # Конфигурация
│   ├── models/              # SQLAlchemy модели
│   ├── routes/              # API и Web routes
│   ├── services/             # Бизнес-логика
│   ├── static/              # CSS, JS
│   └── templates/           # HTML шаблоны
├── migrations/              # Alembic
├── tests/                  # Тесты
├── cli.py                  # CLI интерфейс
├── init_data.py           # Инициализация данных
├── run.py                  # Точка входа
└── requirements.txt
```

## Модели данных

### Category - Категории
- [x] id (UUID)
- [x] name (technename)
- [x] display_name
- [x] description
- [x] icon
- [x] created_at, updated_at

### Object - Объекты
- [x] id (UUID)
- [x] category_id (FK)
- [x] name
- [x] description
- [x] prompt
- [x] image_path
- [x] is_active
- [x] created_at, updated_at

### AttributeDef - Определения атрибутов
- [x] id (UUID)
- [x] category_id (FK)
- [x] name
- [x] display_name
- [x] field_type (bool/int/int_list/str/str_list)
- [x] min_value, max_value, step
- [x] options (JSON)
- [x] is_required

### AttrValue - Значения атрибутов
- [x] id (UUID)
- [x] object_id (FK)
- [x] attribute_def_id (FK)
- [x] bool_value / int_value / str_value

### Template - Шаблоны
- [x] id (UUID)
- [x] name
- [x] description
- [x] template_text
- [x] created_at, updated_at

### TemplateItem - Элементы шаблона
- [x] id (UUID)
- [x] template_id (FK)
- [x] object_id (FK)
- [x] position
- [x] custom_text

### TemplateResult - Результаты
- [x] id (UUID)
- [x] template_id (FK)
- [x] generated_prompt
- [x] image_path
- [x] comfyui_workflow
- [x] created_at

### User - Пользователи
- [x] id (UUID)
- [x] username
- [x] email
- [x] password_hash
- [x] is_admin
- [x] is_active
- [x] created_at, updated_at

## Сервисы

### category_service
- [x] get_all_categories()
- [x] get_category_by_id()
- [x] create_category()
- [x] update_category()
- [x] delete_category()
- [x] get_category_attributes()
- [x] create_category_attribute()

### object_service
- [x] get_all_objects()
- [x] get_object_by_id()
- [x] create_object()
- [x] update_object()
- [x] delete_object()
- [x] add_object_attribute()

### template_service
- [x] get_all_templates()
- [x] get_template_by_id()
- [x] create_template()
- [x] update_template()
- [x] delete_template()
- [x] get_template_items()
- [x] add_template_item()
- [x] delete_template_item()

### generator_service
- [x] generate_prompt()
- [x] get_results()
- [x] get_result_by_id()

### admin_service
- [x] get_stats()
- [x] create_backup()
- [x] list_backups()
- [x] cleanup_unused_images()

### comfyui_service
- [x] send_to_comfyui()
- [x] get_comfyui_status()
- [x] process_webhook()

### auth_service
- [x] get_user_by_id()
- [x] get_user_by_username()
- [x] get_user_by_email()
- [x] create_user()
- [x] update_user()
- [x] delete_user()
- [x] authenticate()
- [x] get_all_users()
- [x] create_admin_user()

## Веб-интерфейс

### Шаблоны (templates/)
- [x] base.html - Базовый шаблон
- [x] index.html - Главная страница
- [x] categories.html - Категории
- [x] objects.html - Объекты
- [x] templates.html - Шаблоны
- [x] generator.html - Генератор
- [x] admin.html - Админ-панель

### Статика (static/)
- [x] css/base.css - Стили
- [x] js/app.js - JavaScript

### Роуты (routes/)
- [x] web.py - Веб-интерфейс
- [x] api.py - REST API
- [x] auth.py - Авторизация

### Шаблоны авторизации
- [x] login.html - Вход
- [x] register.html - Регистрация
- [x] profile.html - Профиль

## Конфигурация

### Параметры в config.py
- [x] SECRET_KEY
- [x] DATABASE_URL
- [x] SERVER_HOST, SERVER_PORT, SERVER_DEBUG
- [x] UPLOAD_DIR, MAX_IMAGE_SIZE
- [x] COMFYUI_HOST, COMFYUI_API_KEY, COMFYUI_TIMEOUT
- [x] BACKUP_DIR, BACKUP_RETENTION_DAYS
- [x] DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT
- [x] DEFAULT_SEEDS, DEFAULT_STEPS, DEFAULT_CFG, DEFAULT_SAMPLER

## Дополнительные компоненты

- [x] CLI интерфейс (cli.py)
- [x] Скрипт инициализации (init_data.py)
- [x] Alembic миграции
- [x] Тесты

## Развертывание (следующий этап)

- [ ] Настройка PostgreSQL
- [ ] Создание пользователя и БД
- [ ] Настройка виртуального окружения
- [ ] Systemd сервис
- [ ] Gunicorn

## Будущий функционал

- [ ] Система дисковых квот для пользователей
- [ ] Токены генерации с лимитами
