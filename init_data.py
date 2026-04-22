from app import create_app, db
from app.services import category_service, object_service, template_service, auth_service


def create_sample_data():
    """Создание примеров данных для демонстрации"""
    
    app = create_app()
    
    with app.app_context():
        print("Создание администратора...")
        try:
            admin = auth_service.create_admin_user(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            print(f"  Создан админ: {admin.username} / admin123")
        except ValueError:
            print("  Админ уже существует")
        
        print("\nСоздание категорий...")
        
        cat_character = category_service.create_category(
            name='character',
            display_name='Персонаж',
            description='Люди, существа, персонажи'
        )
        
        cat_location = category_service.create_category(
            name='location',
            display_name='Локация',
            description='Места, окружение'
        )
        
        cat_action = category_service.create_category(
            name='action',
            display_name='Действие',
            description='Действия, позы, жесты'
        )
        
        cat_clothing = category_service.create_category(
            name='clothing',
            display_name='Одежда',
            description='Одежда, атрибуты'
        )
        
        print(f"  Создано: {cat_character.display_name}, {cat_location.display_name}, {cat_action.display_name}, {cat_clothing.display_name}")
        
        print("\nСоздание атрибутов для категорий...")
        
        category_service.create_category_attribute(
            category_id=cat_character.id,
            name='gender',
            display_name='Пол',
            field_type='str_list',
            options=['мужской', 'женский', 'нейтральный'],
            is_required=False
        )
        
        category_service.create_category_attribute(
            category_id=cat_character.id,
            name='age',
            display_name='Возраст',
            field_type='int_list',
            min_value=1,
            max_value=100,
            step=1,
            is_required=False
        )
        
        category_service.create_category_attribute(
            category_id=cat_character.id,
            name='height',
            display_name='Рост',
            field_type='int_list',
            min_value=100,
            max_value=250,
            step=5,
            is_required=False
        )
        
        category_service.create_category_attribute(
            category_id=cat_character.id,
            name='has_weapon',
            display_name='Оружие',
            field_type='bool',
            is_required=False
        )
        
        print("  Атрибуты персонажа: пол, возраст, рост, оружие")
        
        print("\nСоздание объектов...")
        
        obj_warrior = object_service.create_object(
            category_id=cat_character.id,
            name='Воин',
            description='Сильный воин в броне',
            prompt='warrior, armored, strong, battle-ready'
        )
        
        obj_mage = object_service.create_object(
            category_id=cat_character.id,
            name='Маг',
            description='Мудрый маг в мантии',
            prompt='mage, wizard, robe, magical, mystical'
        )
        
        obj_elf = object_service.create_object(
            category_id=cat_character.id,
            name='Эльф',
            description='Лесной эльф',
            prompt='elf, forest dweller, graceful, pointed ears'
        )
        
        obj_forest = object_service.create_object(
            category_id=cat_location.id,
            name='Лес',
            description='Темный лес',
            prompt='dark forest, mystical trees, fog'
        )
        
        obj_castle = object_service.create_object(
            category_id=cat_location.id,
            name='Замок',
            description='Средневековый замок',
            prompt='castle, medieval fortress, stone walls'
        )
        
        obj_village = object_service.create_object(
            category_id=cat_location.id,
            name='Деревня',
            description='Деревня с хижинами',
            prompt='village, cottages, rustic houses'
        )
        
        obj_walking = object_service.create_object(
            category_id=cat_action.id,
            name='Идет',
            description='Идет пешком',
            prompt='walking, walking pose'
        )
        
        obj_running = object_service.create_object(
            category_id=cat_action.id,
            name='Бежит',
            description='Бежит',
            prompt='running, running pose'
        )
        
        obj_standing = object_service.create_object(
            category_id=cat_action.id,
            name='Стоит',
            description='Стоит',
            prompt='standing, standing pose'
        )
        
        print(f"  Персонажи: {obj_warrior.name}, {obj_mage.name}, {obj_elf.name}")
        print(f"  Локации: {obj_forest.name}, {obj_castle.name}, {obj_village.name}")
        print(f"  Действия: {obj_walking.name}, {obj_running.name}, {obj_standing.name}")
        
        print("\nСоздание шаблонов...")
        
        tmpl1 = template_service.create_template(
            name='Персонаж в локации',
            template_text='{character} {action} in {location}',
            description='Базовый шаблон персонажа в окружении'
        )
        
        template_service.add_template_item(
            template_id=tmpl1.id,
            object_id=obj_warrior.id,
            position=0
        )
        
        template_service.add_template_item(
            template_id=tmpl1.id,
            object_id=obj_walking.id,
            position=1
        )
        
        template_service.add_template_item(
            template_id=tmpl1.id,
            object_id=obj_forest.id,
            position=2
        )
        
        tmpl2 = template_service.create_template(
            name='Воин в замке',
            template_text='{warrior} {action} at {castle}',
            description='Воин у замка'
        )
        
        template_service.add_template_item(
            template_id=tmpl2.id,
            object_id=obj_warrior.id,
            position=0
        )
        
        template_service.add_template_item(
            template_id=tmpl2.id,
            object_id=obj_standing.id,
            position=1
        )
        
        template_service.add_template_item(
            template_id=tmpl2.id,
            object_id=obj_castle.id,
            position=2
        )
        
        print(f"  Шаблоны: {tmpl1.name}, {tmpl2.name}")
        
        print("\nГенерация примеров промтов...")
        
        result1 = template_service.get_template_items(tmpl1.id)
        items_data = [{'object_id': item.object_id, 'custom_text': item.custom_text} for item in result1]
        
        from app.services import generator_service
        
        gen_result1 = generator_service.generate_prompt(tmpl1.id, items_data)
        print(f"  '{tmpl1.name}': {gen_result1['generated_prompt']}")
        
        gen_result2 = generator_service.generate_prompt(tmpl2.id)
        print(f"  '{tmpl2.name}': {gen_result2['generated_prompt']}")
        
        print("\nГотово! Данные созданы.")


if __name__ == '__main__':
    create_sample_data()