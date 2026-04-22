# Prompt Manager

Система хранения и генерации промтов для локальной генерации изображений и видео.

## Технологический стек

- Python 3.11+
- Flask (только app factory)
- SQLAlchemy ORM
- PostgreSQL
- Debian 12+ (без Docker)

## Структура

```
prompt_manager/
├── app/
│   ├── __init__.py      # Flask app factory
│   ├── models/         # SQLAlchemy модели
│   └── services/       # Бизнес-логика (внутренние вызовы)
├── migrations/         # Alembic
├── tests/             # Тесты
├── requirements.txt
└── run.py            # Точка входа
```

## Установка

```bash
# Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка .env
cp .env.example .env
# Отредактируйте .env с настройками БД
```

## Запуск

```bash
# Разработка
python run.py

# Продакшен (gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## Использование

Приложение не предоставляет внешний API. Все взаимодействия — через вызовы сервисов:

```python
from app import create_app, db
from app.services import category_service, object_service, template_service

app = create_app()

with app.app_context():
    # Категории
    cat = category_service.create_category('character', 'Персонаж')
    
    # Объекты
    obj = object_service.create_object(
        category_id=cat.id,
        name='Воин',
        prompt='warrior, armored'
    )
    
    # Шаблоны и генерация
    tmpl = template_service.create_template(
        name='Воин в локации',
        template_text='{obj1} идет в {obj2}',
        items=[{'object_id': obj.id, 'position': 0}]
    )
    
    result = generator_service.generate_prompt(tmpl.id)
```

## Лицензия

MIT