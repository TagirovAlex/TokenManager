import click
from app import create_app, db
from app.services import (
    category_service,
    object_service,
    template_service,
    generator_service,
    admin_service
)


app = create_app()


@click.group()
def cli():
    """Prompt Manager - система управления промтами"""
    pass


@cli.group()
def categories():
    """Управление категориями"""
    pass


@categories.command('list')
def categories_list():
    """Список всех категорий"""
    with app.app_context():
        cats = category_service.get_all_categories()
        if not cats:
            click.echo('Категорий пока нет.')
            return
        for cat in cats:
            click.echo(f"[{cat.id[:8]}] {cat.display_name} ({cat.name})")


@categories.command('create')
@click.argument('name')
@click.argument('display_name')
@click.option('--description', '-d', default='')
@click.option('--icon', '-i', default='')
def categories_create(name, display_name, description, icon):
    """Создать категорию"""
    with app.app_context():
        try:
            cat = category_service.create_category(
                name=name,
                display_name=display_name,
                description=description or None,
                icon=icon or None
            )
            click.echo(f'Создана категория: {cat.display_name} ({cat.id})')
        except ValueError as e:
            click.echo(f'Ошибка: {e}', err=True)


@categories.command('delete')
@click.argument('category_id')
def categories_delete(category_id):
    """Удалить категорию"""
    with app.app_context():
        try:
            category_service.delete_category(category_id)
            click.echo(f'Категория удалена: {category_id}')
        except ValueError as e:
            click.echo(f'Ошибка: {e}', err=True)


@cli.group()
def objects():
    """Управление объектами"""
    pass


@objects.command('list')
@click.option('--category', '-c', help='ID категории')
def objects_list(category):
    """Список всех объектов"""
    with app.app_context():
        objs = object_service.get_all_objects(category_id=category) if category else object_service.get_all_objects()
        if not objs:
            click.echo('Объектов пока нет.')
            return
        for obj in objs:
            click.echo(f"[{obj.id[:8]}] {obj.name} -> {obj.prompt[:50]}...")


@objects.command('create')
@click.argument('category_id')
@click.argument('name')
@click.argument('prompt')
@click.option('--description', '-d', default='')
@click.option('--image', '-i', default='')
def objects_create(category_id, name, prompt, description, image):
    """Создать объект"""
    with app.app_context():
        try:
            obj = object_service.create_object(
                category_id=category_id,
                name=name,
                prompt=prompt,
                description=description or None,
                image_path=image or None
            )
            click.echo(f'Создан объект: {obj.name} ({obj.id})')
        except ValueError as e:
            click.echo(f'Ошибка: {e}', err=True)


@objects.command('delete')
@click.argument('object_id')
def objects_delete(object_id):
    """Удалить объект"""
    with app.app_context():
        try:
            object_service.delete_object(object_id)
            click.echo(f'Объект удален: {object_id}')
        except ValueError as e:
            click.echo(f'Ошибка: {e}', err=True)


@cli.group()
def templates():
    """Управление шаблонами"""
    pass


@templates.command('list')
def templates_list():
    """Список всех шаблонов"""
    with app.app_context():
        tmpls = template_service.get_all_templates()
        if not tmpls:
            click.echo('Шаблонов пока нет.')
            return
        for tmpl in tmpls:
            click.echo(f"[{tmpl.id[:8]}] {tmpl.name}")
            click.echo(f"   Шаблон: {tmpl.template_text}")


@templates.command('create')
@click.argument('name')
@click.argument('template_text')
@click.option('--description', '-d', default='')
def templates_create(name, template_text, description):
    """Создать шаблон"""
    with app.app_context():
        try:
            tmpl = template_service.create_template(
                name=name,
                template_text=template_text,
                description=description or None
            )
            click.echo(f'Создан шаблон: {tmpl.name} ({tmpl.id})')
        except ValueError as e:
            click.echo(f'Ошибка: {e}', err=True)


@templates.command('add-item')
@click.argument('template_id')
@click.argument('object_id')
@click.option('--position', '-p', default=0)
@click.option('--text', '-t', default='')
def templates_add_item(template_id, object_id, position, text):
    """Добавить объект в шаблон"""
    with app.app_context():
        try:
            item = template_service.add_template_item(
                template_id=template_id,
                object_id=object_id,
                position=position,
                custom_text=text or None
            )
            click.echo(f'Добавлен элемент: {item.id}')
        except ValueError as e:
            click.echo(f'Ошибка: {e}', err=True)


@templates.command('delete')
@click.argument('template_id')
def templates_delete(template_id):
    """Удалить шаблон"""
    with app.app_context():
        try:
            template_service.delete_template(template_id)
            click.echo(f'Шаблон удален: {template_id}')
        except ValueError as e:
            click.echo(f'Ошибка: {e}', err=True)


@cli.group()
def generate():
    """Генерация промтов"""
    pass


@generate.command('prompt')
@click.argument('template_id')
@click.option('--save', '-s', is_flag=True, help='Сохранить результат')
def generate_prompt(template_id, save):
    """Сгенерировать промт из шаблона"""
    with app.app_context():
        try:
            result = generator_service.generate_prompt(
                template_id=template_id,
                save_result=save
            )
            click.echo('Сгенерированный промт:')
            click.echo(result['generated_prompt'])
            if 'result_id' in result:
                click.echo(f'\nРезультат сохранен: {result["result_id"]}')
        except ValueError as e:
            click.echo(f'Ошибка: {e}', err=True)


@generate.command('interactive')
def generate_interactive():
    """Интерактивная генерация промта"""
    with app.app_context():
        click.echo('Интерактивная генерация промта')
        click.echo('-' * 40)
        
        categories_list()
        click.echo()
        
        cat_id = click.prompt('Выберите категорию (ID)', type=str)
        
        cats = category_service.get_all_categories()
        selected_cat = next((c for c in cats if c.id == cat_id), None)
        
        if not selected_cat:
            click.echo('Категория не найдена')
            return
        
        objs = object_service.get_all_objects(category_id=cat_id)
        if not objs:
            click.echo('В категории нет объектов')
            return
        
        click.echo('Доступные объекты:')
        for i, obj in enumerate(objs):
            click.echo(f'  {i+1}. {obj.name}')
        
        idx = click.prompt('Выберите объект (номер)', type=int) - 1
        if idx < 0 or idx >= len(objs):
            click.echo('Неверный выбор')
            return
        
        selected_obj = objs[idx]
        click.echo(f'\nВыбран: {selected_obj.name}')
        click.echo(f'Промт: {selected_obj.prompt}')


@cli.group()
def admin():
    """Администрирование"""
    pass


@admin.command('stats')
def admin_stats():
    """Статистика системы"""
    with app.app_context():
        stats = admin_service.get_stats()
        click.echo('Статистика системы:')
        click.echo(f"  Категории: {stats['categories']}")
        click.echo(f"  Объекты: {stats['objects']}")
        click.echo(f"  Шаблоны: {stats['templates']}")
        click.echo(f"  Результаты: {stats['results']}")


@admin.command('backup')
def admin_backup():
    """Создать резервную копию"""
    with app.app_context():
        try:
            backup_dir = app.config.get('BACKUP_DIR')
            upload_dir = app.config.get('UPLOAD_DIR')
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
            
            result = admin_service.create_backup(
                backup_dir=backup_dir,
                upload_dir=upload_dir,
                db_uri=db_uri
            )
            click.echo(f'Бэкап создан: {result["backup_file"]}')
        except Exception as e:
            click.echo(f'Ошибка: {e}', err=True)


if __name__ == '__main__':
    cli()