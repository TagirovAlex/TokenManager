from app import db
from app.models import Template, TemplateItem, Object, TemplateResult


def generate_prompt(template_id, items_data=None, save_result=False, 
                   image_path=None, comfyui_workflow=None):
    template = db.session.get(Template, template_id)
    if not template:
        raise ValueError('Template not found')
    
    if items_data:
        items = items_data
    else:
        template_items = TemplateItem.query.filter_by(template_id=template_id).order_by(TemplateItem.position).all()
        items = [{'object_id': item.object_id, 'custom_text': item.custom_text} for item in template_items]
    
    generated_text = template.template_text
    
    for item_info in items:
        obj = db.session.get(Object, item_info['object_id'])
        if obj:
            placeholder = '{' + item_info['object_id'] + '}'
            if item_info.get('custom_text'):
                generated_text = generated_text.replace(placeholder, 
                    f"{obj.prompt} {item_info['custom_text']}")
            else:
                generated_text = generated_text.replace(placeholder, obj.prompt)
    
    result_data = {'generated_prompt': generated_text}
    
    if save_result:
        result = TemplateResult(
            template_id=template.id,
            generated_prompt=generated_text,
            image_path=image_path,
            comfyui_workflow=comfyui_workflow
        )
        db.session.add(result)
        db.session.commit()
        result_data['result_id'] = result.id
    
    return result_data


def get_results(template_id=None):
    query = TemplateResult.query
    if template_id:
        query = query.filter_by(template_id=template_id)
    return query.order_by(TemplateResult.created_at.desc()).all()


def get_result_by_id(result_id):
    return db.session.get(TemplateResult, result_id)
