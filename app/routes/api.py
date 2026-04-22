from flask import Blueprint, jsonify, request
from app.services import (
    category_service,
    object_service,
    template_service,
    generator_service,
    admin_service,
    comfyui_service
)

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/categories', methods=['GET'])
def get_categories():
    cats = category_service.get_all_categories()
    return jsonify([c.to_dict() for c in cats])


@api.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    try:
        cat = category_service.create_category(
            name=data['name'],
            display_name=data['display_name'],
            description=data.get('description'),
            icon=data.get('icon')
        )
        return jsonify(cat.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    cat = category_service.get_category_by_id(category_id)
    if not cat:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(cat.to_dict())


@api.route('/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.get_json()
    try:
        cat = category_service.update_category(category_id, **data)
        return jsonify(cat.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    try:
        category_service.delete_category(category_id)
        return jsonify({'message': 'Deleted'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/objects', methods=['GET'])
def get_objects():
    category_id = request.args.get('category_id')
    objs = object_service.get_all_objects(category_id=category_id)
    return jsonify([o.to_dict() for o in objs])


@api.route('/objects', methods=['POST'])
def create_object():
    data = request.get_json()
    try:
        obj = object_service.create_object(
            category_id=data['category_id'],
            name=data['name'],
            prompt=data['prompt'],
            description=data.get('description'),
            image_path=data.get('image_path')
        )
        return jsonify(obj.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/objects/<object_id>', methods=['GET'])
def get_object(object_id):
    obj = object_service.get_object_by_id(object_id)
    if not obj:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(obj.to_dict())


@api.route('/objects/<object_id>', methods=['PUT'])
def update_object(object_id):
    data = request.get_json()
    try:
        obj = object_service.update_object(object_id, **data)
        return jsonify(obj.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/objects/<object_id>', methods=['DELETE'])
def delete_object(object_id):
    try:
        object_service.delete_object(object_id)
        return jsonify({'message': 'Deleted'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/templates', methods=['GET'])
def get_templates():
    tmpls = template_service.get_all_templates()
    return jsonify([t.to_dict() for t in tmpls])


@api.route('/templates', methods=['POST'])
def create_template():
    data = request.get_json()
    try:
        tmpl = template_service.create_template(
            name=data['name'],
            template_text=data['template_text'],
            description=data.get('description'),
            items=data.get('items')
        )
        return jsonify(tmpl.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/templates/<template_id>', methods=['GET'])
def get_template(template_id):
    tmpl = template_service.get_template_by_id(template_id)
    if not tmpl:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(tmpl.to_dict())


@api.route('/templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    data = request.get_json()
    try:
        tmpl = template_service.update_template(template_id, **data)
        return jsonify(tmpl.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/templates/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    try:
        template_service.delete_template(template_id)
        return jsonify({'message': 'Deleted'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    try:
        result = generator_service.generate_prompt(
            template_id=data['template_id'],
            items_data=data.get('items'),
            save_result=data.get('save_result', False)
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api.route('/results', methods=['GET'])
def get_results():
    template_id = request.args.get('template_id')
    results = generator_service.get_results(template_id=template_id)
    return jsonify([r.to_dict() for r in results])


@api.route('/stats', methods=['GET'])
def get_stats():
    stats = admin_service.get_stats()
    return jsonify(stats)


@api.route('/comfyui/send', methods=['POST'])
def send_to_comfyui():
    data = request.get_json()
    from flask import current_app
    try:
        result = comfyui_service.send_to_comfyui(
            prompt=data['prompt'],
            comfyui_host=current_app.config.get('COMFYUI_HOST'),
            api_key=current_app.config.get('COMFYUI_API_KEY'),
            timeout=current_app.config.get('COMFYUI_TIMEOUT')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/comfyui/webhook', methods=['POST'])
def comfyui_webhook():
    data = request.get_json()
    result = comfyui_service.process_webhook(data)
    return jsonify(result)