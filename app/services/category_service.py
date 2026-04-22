from app import db
from app.models import Category, AttributeDef, CategoryAttribute


def get_all_categories():
    return Category.query.all()


def get_category_by_id(category_id):
    return db.session.get(Category, category_id)


def create_category(name, display_name, description=None, icon=None, image_path=None):
    if Category.query.filter_by(name=name).first():
        raise ValueError('Category with this name already exists')
    
    category = Category(
        name=name,
        display_name=display_name,
        description=description,
        icon=icon,
        image_path=image_path
    )
    db.session.add(category)
    db.session.commit()
    return category


def update_category(category_id, **kwargs):
    category = db.session.get(Category, category_id)
    if not category:
        raise ValueError('Category not found')
    
    if 'name' in kwargs:
        existing = Category.query.filter_by(name=kwargs['name']).first()
        if existing and existing.id != category_id:
            raise ValueError('Category name already exists')
        category.name = kwargs['name']
    
    for field in ['display_name', 'description', 'icon', 'image_path']:
        if field in kwargs:
            setattr(category, field, kwargs[field])
    
    db.session.commit()
    return category


def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        raise ValueError('Category not found')
    
    if category.objects.count() > 0:
        raise ValueError(f'Cannot delete category: contains {category.objects.count()} objects. Delete objects first.')
    
    db.session.delete(category)
    db.session.commit()


def get_category_attributes(category_id):
    links = CategoryAttribute.query.filter_by(category_id=category_id).all()
    return [link.attribute_def for link in links]


def get_all_attributes():
    return AttributeDef.query.all()


def create_attribute(name, display_name, field_type, 
                   min_value=None, max_value=None, step=None, 
                   options=None, is_required=False):
    if field_type not in AttributeDef.FIELD_TYPES:
        raise ValueError(f'Invalid field_type: {field_type}')
    
    attr = AttributeDef(
        name=name,
        display_name=display_name,
        field_type=field_type,
        min_value=min_value,
        max_value=max_value,
        step=step,
        options=options,
        is_required=is_required
    )
    db.session.add(attr)
    db.session.commit()
    return attr


def update_attribute(attribute_id, **kwargs):
    attr = db.session.get(AttributeDef, attribute_id)
    if not attr:
        raise ValueError('Attribute not found')
    
    for field in ['name', 'display_name', 'field_type', 'min_value', 'max_value', 'step', 'options', 'is_required']:
        if field in kwargs:
            setattr(attr, field, kwargs[field])
    
    db.session.commit()
    return attr


def delete_attribute(attribute_id):
    attr = db.session.get(AttributeDef, attribute_id)
    if not attr:
        raise ValueError('Attribute not found')
    
    db.session.delete(attr)
    db.session.commit()


def link_attribute_to_category(attribute_id, category_id):
    existing = CategoryAttribute.query.filter_by(
        attribute_def_id=attribute_id,
        category_id=category_id
    ).first()
    if existing:
        raise ValueError('Attribute already linked to category')
    
    link = CategoryAttribute(
        attribute_def_id=attribute_id,
        category_id=category_id
    )
    db.session.add(link)
    db.session.commit()
    return link


def unlink_attribute_from_category(attribute_id, category_id):
    link = CategoryAttribute.query.filter_by(
        attribute_def_id=attribute_id,
        category_id=category_id
    ).first()
    if not link:
        raise ValueError('Link not found')
    
    db.session.delete(link)
    db.session.commit()


def create_category_attribute(category_id, name, display_name, field_type, 
                         min_value=None, max_value=None, step=None, 
                         options=None, is_required=False):
    attr = create_attribute(name, display_name, field_type, 
                          min_value, max_value, step, 
                          options, is_required)
    link_attribute_to_category(attr.id, category_id)
    return attr