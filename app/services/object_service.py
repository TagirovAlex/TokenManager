from app import db
from app.models import Object, AttrValue, TemplateItem


def get_all_objects(category_id=None, is_active=None):
    query = Object.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    
    return query.all()


def get_object_by_id(object_id):
    return db.session.get(Object, object_id)


def create_object(category_id, name, prompt, description=None, 
                  image_path=None, is_active=True, attributes=None):
    if not category_id or not name or not prompt:
        raise ValueError('category_id, name and prompt are required')
    
    obj = Object(
        category_id=category_id,
        name=name,
        description=description,
        prompt=prompt,
        image_path=image_path,
        is_active=is_active
    )
    db.session.add(obj)
    db.session.commit()
    
    if attributes:
        for attr_data in attributes:
            attr_value = AttrValue(
                object_id=obj.id,
                attribute_def_id=attr_data['attribute_def_id'],
                bool_value=attr_data.get('bool_value'),
                int_value=attr_data.get('int_value'),
                str_value=attr_data.get('str_value')
            )
            db.session.add(attr_value)
        db.session.commit()
    
    return obj


def update_object(object_id, **kwargs):
    obj = db.session.get(Object, object_id)
    if not obj:
        raise ValueError('Object not found')
    
    for field in ['name', 'description', 'prompt', 'image_path', 'is_active', 'category_id']:
        if field in kwargs:
            setattr(obj, field, kwargs[field])
    
    db.session.commit()
    return obj


def get_object_references(object_id):
    from app.models import Template, TemplateResult
    refs = []
    
    items = TemplateItem.query.filter_by(object_id=object_id).all()
    for item in items:
        template = Template.query.get(item.template_id)
        if template:
            refs.append(f'Шаблон "{template.name}"')
    
    return refs


def delete_object(object_id):
    obj = db.session.get(Object, object_id)
    if not obj:
        raise ValueError('Object not found')
    
    refs = get_object_references(object_id)
    if refs:
        raise ValueError(f'Object is used in: {", ".join(refs)}')
    
    db.session.delete(obj)
    db.session.commit()


def add_object_attribute(object_id, attribute_def_id, bool_value=None, 
                        int_value=None, str_value=None):
    obj = db.session.get(Object, object_id)
    if not obj:
        raise ValueError('Object not found')
    
    attr_value = AttrValue(
        object_id=object_id,
        attribute_def_id=attribute_def_id,
        bool_value=bool_value,
        int_value=int_value,
        str_value=str_value
    )
    db.session.add(attr_value)
    db.session.commit()
    return attr_value
