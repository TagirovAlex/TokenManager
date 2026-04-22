# Prompt Manager

Система хранения и генерации промтов для локальной генерации изображений и видео.
Навйбкодена бесплатными инструментами чисто для себя, что бы удобно хранить промты генераций для ComfyUI

## Возможности

- **Категории** — создавайте и редактируйте категории объектов (персонажи, локации, одежда, транспорт и др.)
- **Объекты** — храните объекты с промтами и изображениями
- **Реквизиты (независимая сущность)** — гибкая система полей, привязывается к категориям через связи
- **Шаблоны** — создавайте шаблоны для автоматической генерации промтов
- **Интерактивный генератор** — добавляйте объекты и текст в промт, редактируйте результат
- **Интеграция с ComfyUI** — отправляйте сгенерированные промты напрямую в ComfyUI
- **Веб-интерфейс** — удобное управление через браузер
- **Администрирование** — бэкапы, статистика, очистка изображений

## Технологический стек

| Компонент | Версия |
|-----------|--------|
| Python | 3.11+ |
| Flask | 2.x |
| SQLAlchemy | ORM |
| PostgreSQL | 15+ |
| Gunicorn | WSGI-сервер |
| Debian | 12+ (без Docker) |

## Структура проекта

```
TokenManager/
├── app/
│   ├── __init__.py            # Flask App Factory
│   ├── config.py              # Конфигурация
│   ├── models/
│   │   └── __init__.py        # SQLAlchemy модели (Category, Object, AttributeDef, CategoryAttribute, AttrValue, Template, TemplateItem, TemplateResult, User)
│   ├── routes/
│   │   ├── web.py            # Основные маршруты
│   │   └── auth.py           # Аутентификация
│   ├── services/
│   │   ├── category_service.py
│   │   ├── object_service.py
│   │   ├── template_service.py
│   │   ├── generator_service.py
│   │   ├── admin_service.py
│   │   ├── auth_service.py
│   │   └── comfyui_service.py
│   ├── static/
│   │   └── css/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── profile.html
│   │   ├── categories.html
│   │   ├── category_detail.html
│   │   ├── category_edit.html
│   │   ├── objects.html
│   │   ├── object_edit.html
│   │   ├── attributes.html         # Все реквизиты
│   │   ├── attribute_list.html    # Реквизиты категории
│   │   ├── attribute_edit.html
│   │   ├── templates.html
│   │   ├── template_edit.html
│   │   ├── generator.html
│   │   ├── admin.html
│   │   └── index.html
│   └── utils/
├── migrations/                # Alembic миграции
├── tests/                      # Тесты
├── requirements.txt
├── run.py                       # Точка входа
└── .env                        # Переменные окружения (локальный)
```

## Модели данных

### Category (Категории)

Типы объектов: персонаж, локация, действие, одежда, транспорт, архитектура и др.

- `id` — UUID (первичный ключ)
- `name` — техническое имя (уникальное)
- `display_name` — отображаемое имя
- `description` — описание
- `icon` — иконка

### Object (Объекты)

Конкретные сущности внутри категории.

- `id` — UUID
- `category_id` — связь с категорией
- `name` — имя объекта
- `prompt` — текстовая часть промта
- `image_path` — путь к изображению
- `is_active` — активен/неактивен

### AttributeDef (Реквизиты)

Независимая сущность - дополнительные поля для объектов. Может быть привязана к одной или нескольким категориям через таблицу связей.

Типы полей:
- `bool` — да/нет
- `int` — целое число
- `int_list` — число из диапазона (min, max, step)
- `str` — строка
- `str_list` — строка из списка вариантов

### CategoryAttribute (Связь категории-реквизита)

Таблица связей между категориями и реквизитами (многие-ко-многим).

### AttrValue (Значения реквизитов)

Значения реквизитов для конкретных объектов.

### Template (Шаблоны)

Шаблоны для генерации промтов с поддержкой плейсхолдеров `{object_id}`.

### TemplateResult (Результаты)

Сохраненные результаты генерации промтов.

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/TagirovAlex/TokenManager.git
cd TokenManager
```

### 2. Создание виртуального окружения

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

```bash
cp .env.example .env
# Отредактируйте .env с настройками БД
```

Параметры в `.env`:
```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
SERVER_DEBUG=False

# Для загрузки изображений
UPLOAD_DIR=/var/lib/prompt_manager/uploads
MAX_IMAGE_SIZE=10485760

# ComfyUI (опционально)
COMFYUI_HOST=http://localhost:8188
COMFYUI_API_KEY=

# Бэкапы
BACKUP_DIR=/var/backups/prompt_manager
BACKUP_RETENTION_DAYS=30
```

### 5. Инициализация базы данных

База данных создается автоматически при первом запуске приложения.

```bash
# Загрузка начальных данных (опционально)
python init_data.py
```

## Запуск

### Режим разработки

```bash
python run.py
```

Приложение будет доступно по адресу `http://localhost:5000`

### Режим продакшена

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## Развертывание на сервере

### Автоматическая установка

```bash
# Запуск от имени root
sudo bash install.sh
```

Скрипт `install.sh` выполняет:
1. Установку системных зависимостей
2. Создание пользователя `prompt`
3. Настройку директорий
4. Установку Python-зависимостей
5. Настройку PostgreSQL
6. Клонирование/обновление проекта
7. Применение миграций
8. Настройку systemd-сервиса
9. Конфигурацию nginx

### Ручная установка

1. Создайте директории:
   ```bash
   sudo mkdir -p /opt/prompt_manager
   sudo mkdir -p /var/lib/prompt_manager/uploads
   sudo mkdir -p /var/backups/prompt_manager
   ```

2. Скопируйте файлы проекта в `/opt/prompt_manager`

3. Настройте PostgreSQL:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE prompt_manager;
   CREATE USER prompt_user WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE prompt_manager TO prompt_user;
   ```

4. Установите зависимости и примените миграции

5. Настройте systemd-сервис:
   ```bash
   sudo cp deploy/prompt_manager.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable prompt_manager
   sudo systemctl start prompt_manager
   ```

6. Настройте nginx:
   ```bash
   sudo cp deploy/nginx.conf /etc/nginx/sites-available/prompt_manager
   sudo ln -s /etc/nginx/sites-available/prompt_manager /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

## Использование

### Веб-интерфейс

После запуска откройте `http://localhost:5000` в браузере.

Функции:
- `/` — главная страница
- `/login` — вход
- `/register` — регистрация
- `/categories` — управление категориями
- `/objects` — управление объектами
- `/templates` — управление шаблонами
- `/generator` — генератор промтов
- `/profile` — профиль пользователя
- `/admin` — администрирование (для админов)

### Программный доступ

```python
from app import create_app, db
from app.services import category_service, object_service, template_service, generator_service

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
    
    # Создание шаблона
    tmpl = template_service.create_template(
        name='Персонаж в локации',
        template_text='{char} идет в {loc}',
        items=[
            {'object_id': char_obj.id, 'position': 0, 'placeholder': 'char'},
            {'object_id': loc_obj.id, 'position': 1, 'placeholder': 'loc'}
        ]
    )
    
    # Генерация промта
    result = generator_service.generate_prompt(tmpl.id)
    print(result['generated_prompt'])
```

## Конфигурация

Все настройки хранятся в `app/config.py` и читаются из переменных окружения.

| Параметр | Переменная | По умолчанию |
|----------|------------|--------------|
| SECRET_KEY | SECRET_KEY | dev-secret-key |
| DATABASE_URL | DATABASE_URL | postgresql://... |
| SERVER_HOST | SERVER_HOST | 0.0.0.0 |
| SERVER_PORT | SERVER_PORT | 5000 |
| UPLOAD_DIR | UPLOAD_DIR | /var/lib/prompt_manager/uploads |
| MAX_IMAGE_SIZE | MAX_IMAGE_SIZE | 10485760 |
| COMFYUI_HOST | COMFYUI_HOST | http://localhost:8188 |
| BACKUP_DIR | BACKUP_DIR | /var/backups/prompt_manager |
| DEFAULT_IMAGE_WIDTH | DEFAULT_IMAGE_WIDTH | 512 |
| DEFAULT_IMAGE_HEIGHT | DEFAULT_IMAGE_HEIGHT | 512 |
| DEFAULT_STEPS | DEFAULT_STEPS | 20 |
| DEFAULT_CFG | DEFAULT_CFG | 8 |
| DEFAULT_SAMPLER | DEFAULT_SAMPLER | euler |

## Требования

- Python 3.11+
- PostgreSQL 15+
- Debian 12+ (или другой Linux-дистрибутив)
- nginx (для продакшена)
- systemd (для управления сервисом)

## Лицензия

MIT
