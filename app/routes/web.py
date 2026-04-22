from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app import db
from app.services import (
    category_service,
    object_service,
    template_service,
    generator_service,
    admin_service
)
from app.utils.image_utils import allowed_file, process_and_save_image, generate_image_filename

web = Blueprint('web', __name__)


@web.route('/')
def index():
    stats = admin_service.get_stats()
    return render_template('admin.html', stats=stats)


@web.route('/categories')
def categories():
    cats = category_service.get_all_categories()
    return render_template('categories.html', categories=cats)


@web.route('/categories/create', methods=['POST'])
def category_create():
    try:
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                temp_id = f"cat_{datetime.now().timestamp()}"
                filename = generate_image_filename(file.filename, temp_id)
                upload_dir = current_app.config.get('UPLOAD_DIR', '/var/lib/prompt_manager/uploads')
                image_path = process_and_save_image(file, upload_dir, filename)
        
        category_service.create_category(
            name=request.form['name'],
            display_name=request.form['display_name'],
            description=request.form.get('description'),
            icon=request.form.get('icon'),
            image_path=image_path
        )
        flash('Категория создана', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('web.categories'))


@web.route('/categories/<category_id>/edit')
def category_edit(category_id):
    cat = category_service.get_category_by_id(category_id)
    if not cat:
        flash('Категория не найдена', 'error')
        return redirect(url_for('web.categories'))
    attrs = category_service.get_category_attributes(category_id)
    return render_template('category_edit.html', category=cat, attributes=attrs, category_service=category_service)


@web.route('/categories/<category_id>/update', methods=['POST'])
def category_update(category_id):
    try:
        image_path = None
        keep_image = request.form.get('keep_image') == 'true'
        
        if not keep_image and 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = generate_image_filename(file.filename, category_id)
                upload_dir = current_app.config.get('UPLOAD_DIR', '/var/lib/prompt_manager/uploads')
                image_path = process_and_save_image(file, upload_dir, filename)
        
        update_data = {
            'name': request.form['name'],
            'display_name': request.form['display_name'],
            'description': request.form.get('description'),
            'icon': request.form.get('icon')
        }
        
        if image_path:
            update_data['image_path'] = image_path
        elif keep_image:
            update_data['image_path'] = request.form.get('current_image_path')
        
        category_service.update_category(category_id, **update_data)
        flash('Категория обновлена', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('web.categories'))


@web.route('/categories/<category_id>')
def category_detail(category_id):
    cat = category_service.get_category_by_id(category_id)
    if not cat:
        flash('Категория не найдена', 'error')
        return redirect(url_for('web.categories'))
    
    objs = object_service.get_all_objects(category_id=category_id)
    attrs = category_service.get_category_attributes(category_id)
    return render_template('category_detail.html', category=cat, objects=objs, attributes=attrs)


@web.route('/categories/<category_id>/delete')
def category_delete(category_id):
    try:
        category_service.delete_category(category_id)
        flash('Категория удалена', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('web.categories'))


@web.route('/attributes')
def attributes():
    all_attrs = category_service.get_all_attributes()
    return render_template('attributes.html', attributes=all_attrs)


@web.route('/categories/<category_id>/attributes')
def attribute_list(category_id):
    cat = category_service.get_category_by_id(category_id)
    if not cat:
        flash('Категория не найдена', 'error')
        return redirect(url_for('web.categories'))
    attrs = category_service.get_category_attributes(category_id)
    return render_template('attribute_list.html', category=cat, attributes=attrs)


@web.route('/categories/<category_id>/attributes/create', methods=['POST'])
def attribute_create(category_id):
    try:
        field_type = request.form.get('field_type')
        
        min_value = None
        max_value = None
        step = None
        options = None
        
        if field_type == 'int_list':
            min_value = request.form.get('min_value', type=int)
            max_value = request.form.get('max_value', type=int)
            step = request.form.get('step', type=int)
        
        if field_type == 'str_list':
            options_str = request.form.get('options', '')
            options = [o.strip() for o in options_str.split(',') if o.strip()]
        
        category_service.create_category_attribute(
            category_id=category_id,
            name=request.form['name'],
            display_name=request.form['display_name'],
            field_type=field_type,
            min_value=min_value,
            max_value=max_value,
            step=step,
            options=options,
            is_required=request.form.get('is_required') == 'on'
        )
        flash('Реквизит создан', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('web.category_detail', category_id=category_id))


@web.route('/attributes/<attribute_id>/edit')
def attribute_edit(attribute_id):
    from app.models import AttributeDef
    attr = db.session.get(AttributeDef, attribute_id)
    if not attr:
        flash('Реквизит не найден', 'error')
        return redirect(url_for('web.categories'))
    return render_template('attribute_edit.html', attribute=attr)


@web.route('/attributes/<attribute_id>/update', methods=['POST'])
def attribute_update(attribute_id):
    try:
        from app.models import AttributeDef
        attr = db.session.get(AttributeDef, attribute_id)
        if not attr:
            flash('Реквизит не найден', 'error')
            return redirect(url_for('web.categories'))
        
        attr.name = request.form['name']
        attr.display_name = request.form['display_name']
        attr.field_type = request.form['field_type']
        attr.is_required = request.form.get('is_required') == 'on'
        
        if attr.field_type == 'int_list':
            attr.min_value = request.form.get('min_value', type=int)
            attr.max_value = request.form.get('max_value', type=int)
            attr.step = request.form.get('step', type=int)
        
        if attr.field_type == 'str_list':
            options_str = request.form.get('options', '')
            attr.options = [o.strip() for o in options_str.split(',') if o.strip()]
        
        db.session.commit()
        flash('Реквизит обновлен', 'success')
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
    
    return redirect(url_for('web.attribute_list', category_id=attr.category_id))


@web.route('/attributes/<attribute_id>/delete')
def attribute_delete(attribute_id):
    from app.models import AttributeDef
    attr = db.session.get(AttributeDef, attribute_id)
    if not attr:
        flash('Реквизит не найден', 'error')
        return redirect(url_for('web.categories'))
    
    category_id = attr.category_id
    try:
        db.session.delete(attr)
        db.session.commit()
        flash('Реквизит удален', 'success')
    except Exception as e:
        flash(f'Ошибка удаления: {str(e)}', 'error')
    
    return redirect(url_for('web.attribute_list', category_id=category_id))


@web.route('/objects')
def objects():
    category_id = request.args.get('category_id')
    cats = category_service.get_all_categories()
    
    attribute_defs = {}
    for cat in cats:
        attrs = category_service.get_category_attributes(cat.id)
        if attrs:
            attribute_defs[cat.id] = [a.to_dict() for a in attrs]
    
    if category_id:
        objs = object_service.get_all_objects(category_id=category_id)
    else:
        objs = object_service.get_all_objects()
    
    return render_template('objects.html', objects=objs, categories=cats, selected_category=category_id, attribute_defs=attribute_defs)


@web.route('/objects/create', methods=['POST'])
def object_create():
    try:
        image_path = request.form.get('image_path')
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                category_id = request.form['category_id']
                temp_id = f"temp_{datetime.now().timestamp()}"
                filename = generate_image_filename(file.filename, temp_id)
                upload_dir = current_app.config.get('UPLOAD_DIR', '/var/lib/prompt_manager/uploads')
                image_path = process_and_save_image(file, upload_dir, filename)
        
        attributes = []
        for key, value in request.form.items():
            if key.startswith('attr_') and value:
                attr_id = key.replace('attr_', '')
                attr_data = {
                    'attribute_def_id': attr_id
                }
                if value == 'true':
                    attr_data['bool_value'] = True
                elif value == 'false':
                    attr_data['bool_value'] = False
                elif value.isdigit():
                    attr_data['int_value'] = int(value)
                else:
                    attr_data['str_value'] = value
                attributes.append(attr_data)
        
        obj = object_service.create_object(
            category_id=request.form['category_id'],
            name=request.form['name'],
            prompt=request.form['prompt'],
            description=request.form.get('description'),
            image_path=image_path,
            attributes=attributes if attributes else None
        )
        flash('Объект создан', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    cat_id = request.form.get('category_id')
    if cat_id:
        return redirect(url_for('web.category_detail', category_id=cat_id))
    return redirect(url_for('web.objects'))


@web.route('/objects/edit/<object_id>')
def object_edit(object_id):
    obj = object_service.get_object_by_id(object_id)
    if not obj:
        flash('Объект не найден', 'error')
        return redirect(url_for('web.objects'))
    
    cats = category_service.get_all_categories()
    attrs = category_service.get_category_attributes(obj.category_id)
    return render_template('object_edit.html', object=obj, categories=cats, attributes=attrs)


@web.route('/objects/update/<object_id>', methods=['POST'])
def object_update(object_id):
    try:
        keep_image = request.form.get('keep_image') == 'true'
        image_path = None if not keep_image else request.form.get('image_path')
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = generate_image_filename(file.filename, object_id)
                upload_dir = current_app.config.get('UPLOAD_DIR', '/var/lib/prompt_manager/uploads')
                image_path = process_and_save_image(file, upload_dir, filename)
        
        object_service.update_object(
            object_id=object_id,
            name=request.form['name'],
            prompt=request.form['prompt'],
            description=request.form.get('description'),
            image_path=image_path,
            category_id=request.form['category_id']
        )
        
        from app.models import AttrValue, AttributeDef
        existing = AttrValue.query.filter_by(object_id=object_id).all()
        for av in existing:
            db.session.delete(av)
        db.session.commit()
        
        for key, value in request.form.items():
            if key.startswith('attr_') and value:
                attr_id = key.replace('attr_', '')
                attr_data = {'attribute_def_id': attr_id, 'object_id': object_id}
                if value == 'true':
                    attr_data['bool_value'] = True
                elif value == 'false':
                    attr_data['bool_value'] = False
                elif value.isdigit():
                    attr_data['int_value'] = int(value)
                else:
                    attr_data['str_value'] = value
                av = AttrValue(**attr_data)
                db.session.add(av)
        db.session.commit()
        
        flash('Объект обновлен', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    obj = object_service.get_object_by_id(object_id)
    if obj:
        return redirect(url_for('web.category_detail', category_id=obj.category_id))
    return redirect(url_for('web.objects'))


@web.route('/objects/delete/<object_id>')
def object_delete(object_id):
    try:
        object_service.delete_object(object_id)
        flash('Объект удален', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('web.objects'))


@web.route('/templates')
def templates():
    tmpls = template_service.get_all_templates()
    for tmpl in tmpls:
        items = template_service.get_template_items(tmpl.id)
        tmpl.items = items
    return render_template('templates.html', templates=tmpls)


@web.route('/templates/create', methods=['POST'])
def template_create():
    try:
        template_service.create_template(
            name=request.form['name'],
            template_text=request.form['template_text'],
            description=request.form.get('description')
        )
        flash('Шаблон создан', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('web.templates'))


@web.route('/templates/edit/<template_id>')
def template_edit(template_id):
    tmpl = template_service.get_template_by_id(template_id)
    if not tmpl:
        flash('Шаблон не найден', 'error')
        return redirect(url_for('web.templates'))
    
    items = template_service.get_template_items(template_id)
    objs = object_service.get_all_objects()
    cats = category_service.get_all_categories()
    return render_template('template_edit.html', template=tmpl, items=items, objects=objs, categories=cats)


@web.route('/templates/update/<template_id>', methods=['POST'])
def template_update(template_id):
    try:
        template_service.update_template(
            template_id=template_id,
            name=request.form['name'],
            template_text=request.form['template_text'],
            description=request.form.get('description')
        )
        flash('Шаблон обновлен', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('web.templates'))


@web.route('/templates/delete/<template_id>')
def template_delete(template_id):
    try:
        template_service.delete_template(template_id)
        flash('Шаблон удален', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('web.templates'))


@web.route('/templates/<template_id>/add-item', methods=['POST'])
def template_add_item(template_id):
    try:
        template_service.add_template_item(
            template_id=template_id,
            object_id=request.form['object_id'],
            position=int(request.form.get('position', 0)),
            custom_text=request.form.get('custom_text')
        )
        flash('Элемент добавлен', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    return redirect(url_for('web.template_edit', template_id=template_id))


@web.route('/generator', methods=['GET', 'POST'])
def generator():
    cats = category_service.get_all_categories()
    objs = object_service.get_all_objects()
    tmpls = template_service.get_all_templates()
    
    generated_prompt = None
    
    if request.method == 'POST':
        template_id = request.form.get('template_id')
        if template_id:
            items_data = []
            for key in request.form:
                if key.startswith('object_'):
                    obj_id = key.replace('object_', '')
                    items_data.append({
                        'object_id': obj_id,
                        'custom_text': request.form.get(f'text_{obj_id}', '')
                    })
            
            try:
                result = generator_service.generate_prompt(
                    template_id=template_id,
                    items_data=items_data if items_data else None
                )
                generated_prompt = result['generated_prompt']
            except ValueError as e:
                flash(str(e), 'error')
    
    return render_template('generator.html', 
                         categories=cats, 
                         objects=objs, 
                         templates=tmpls,
                         generated_prompt=generated_prompt)


@web.route('/generate', methods=['POST'])
def generate():
    template_id = request.form.get('template_id')
    items = []
    
    for key in request.form:
        if key.startswith('obj_'):
            obj_id = key.replace('obj_', '')
            items.append({
                'object_id': obj_id,
                'custom_text': request.form.get(f'text_{obj_id}', '')
            })
    
    try:
        result = generator_service.generate_prompt(
            template_id=template_id,
            items_data=items if items else None
        )
        flash('Промт сгенерирован', 'success')
        return redirect(url_for('web.generator', generated=result['generated_prompt']))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('web.generator'))


@web.route('/admin')
def admin():
    from flask import current_app
    stats = admin_service.get_stats()
    backups = admin_service.list_backups(current_app.config.get('BACKUP_DIR'))
    return render_template('admin.html', 
                         stats=stats, 
                         backups=backups,
                         config=current_app.config)


@web.route('/admin/backup', methods=['POST'])
def backup_create():
    from flask import current_app
    try:
        backup_dir = current_app.config.get('BACKUP_DIR')
        upload_dir = current_app.config.get('UPLOAD_DIR')
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        
        result = admin_service.create_backup(backup_dir, upload_dir, db_uri)
        flash(f'Бэкап создан: {result["backup_file"]}', 'success')
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
    return redirect(url_for('web.admin'))


@web.route('/admin/cleanup', methods=['POST'])
def cleanup_images():
    from flask import current_app
    try:
        upload_dir = current_app.config.get('UPLOAD_DIR')
        result = admin_service.cleanup_unused_images(upload_dir)
        flash(f'Удалено файлов: {result["deleted"]}', 'success')
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
    return redirect(url_for('web.admin'))


@web.route('/comfyui/send')
def comfyui_send():
    prompt = request.args.get('prompt', '')
    from flask import current_app
    try:
        from app.services import comfyui_service
        result = comfyui_service.send_to_comfyui(
            prompt=prompt,
            comfyui_host=current_app.config.get('COMFYUI_HOST'),
            api_key=current_app.config.get('COMFYUI_API_KEY')
        )
        flash(f'Отправлено в ComfyUI. ID: {result.get("prompt_id")}', 'success')
    except Exception as e:
        flash(f'Ошибка: {str(e)}', 'error')
    return redirect(url_for('web.generator'))