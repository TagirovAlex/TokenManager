from app import db
from app.models import Template, TemplateItem


def get_all_templates():
    return Template.query.all()


def get_template_by_id(template_id):
    return db.session.get(Template, template_id)


def create_template(name, template_text, description=None, items=None):
    if not name or not template_text:
        raise ValueError('name and template_text are required')
    
    template = Template(
        name=name,
        description=description,
        template_text=template_text
    )
    db.session.add(template)
    db.session.commit()
    
    if items:
        for item_data in items:
            item = TemplateItem(
                template_id=template.id,
                object_id=item_data['object_id'],
                position=item_data.get('position', 0),
                custom_text=item_data.get('custom_text')
            )
            db.session.add(item)
        db.session.commit()
    
    return template


def update_template(template_id, **kwargs):
    template = db.session.get(Template, template_id)
    if not template:
        raise ValueError('Template not found')
    
    for field in ['name', 'description', 'template_text']:
        if field in kwargs:
            setattr(template, field, kwargs[field])
    
    db.session.commit()
    return template


def delete_template(template_id):
    template = db.session.get(Template, template_id)
    if not template:
        raise ValueError('Template not found')
    db.session.delete(template)
    db.session.commit()


def get_template_items(template_id):
    return TemplateItem.query.filter_by(template_id=template_id).order_by(TemplateItem.position).all()


def add_template_item(template_id, object_id, position=0, custom_text=None):
    item = TemplateItem(
        template_id=template_id,
        object_id=object_id,
        position=position,
        custom_text=custom_text
    )
    db.session.add(item)
    db.session.commit()
    return item


def delete_template_item(item_id):
    item = db.session.get(TemplateItem, item_id)
    if not item:
        raise ValueError('TemplateItem not found')
    db.session.delete(item)
    db.session.commit()


def remove_template_item(item_id):
    delete_template_item(item_id)