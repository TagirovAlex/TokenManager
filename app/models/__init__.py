import uuid
from datetime import datetime
from app import db


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    image_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    objects = db.relationship('Object', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    attribute_links = db.relationship('CategoryAttribute', backref='category', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'icon': self.icon,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'objects_count': self.objects.count(),
            'attributes_count': self.attribute_links.count()
        }


class Object(db.Model):
    __tablename__ = 'objects'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    prompt = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    attr_values = db.relationship('AttrValue', backref='object', lazy='dynamic', cascade='all, delete-orphan')
    template_items = db.relationship('TemplateItem', backref='object', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'prompt': self.prompt,
            'image_path': self.image_path,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'attributes': [av.to_dict() for av in self.attr_values]
        }


class AttributeDef(db.Model):
    __tablename__ = 'attribute_defs'
    
    FIELD_TYPES = ['bool', 'int', 'int_list', 'str', 'str_list']
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(255), nullable=False)
    field_type = db.Column(db.String(20), nullable=False)
    min_value = db.Column(db.Integer)
    max_value = db.Column(db.Integer)
    step = db.Column(db.Integer)
    options = db.Column(db.JSON)
    is_required = db.Column(db.Boolean, default=False)
    
    category_links = db.relationship('CategoryAttribute', backref='attribute_def', lazy='dynamic', cascade='all, delete-orphan')
    attr_values = db.relationship('AttrValue', backref='attribute_def', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'field_type': self.field_type,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'step': self.step,
            'options': self.options,
            'is_required': self.is_required
        }


class CategoryAttribute(db.Model):
    __tablename__ = 'category_attributes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False)
    attribute_def_id = db.Column(db.String(36), db.ForeignKey('attribute_defs.id'), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('category_id', 'attribute_def_id', name='uq_category_attribute'),
    )


class AttrValue(db.Model):
    __tablename__ = 'attr_values'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    object_id = db.Column(db.String(36), db.ForeignKey('objects.id'), nullable=False)
    attribute_def_id = db.Column(db.String(36), db.ForeignKey('attribute_defs.id'), nullable=False)
    bool_value = db.Column(db.Boolean)
    int_value = db.Column(db.Integer)
    str_value = db.Column(db.String(500))
    
    def to_dict(self):
        result = {'id': self.id, 'attribute_def_id': self.attribute_def_id}
        if self.bool_value is not None:
            result['value'] = self.bool_value
        elif self.int_value is not None:
            result['value'] = self.int_value
        elif self.str_value is not None:
            result['value'] = self.str_value
        return result


class Template(db.Model):
    __tablename__ = 'templates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    template_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship('TemplateItem', backref='template', lazy='dynamic', cascade='all, delete-orphan')
    results = db.relationship('TemplateResult', backref='template', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template_text': self.template_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }


class TemplateItem(db.Model):
    __tablename__ = 'template_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.String(36), db.ForeignKey('templates.id'), nullable=False)
    object_id = db.Column(db.String(36), db.ForeignKey('objects.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    custom_text = db.Column(db.String(500))
    
    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'object_id': self.object_id,
            'object_name': self.object.name if self.object else None,
            'object_prompt': self.object.prompt if self.object else None,
            'position': self.position,
            'custom_text': self.custom_text
        }


class TemplateResult(db.Model):
    __tablename__ = 'template_results'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.String(36), db.ForeignKey('templates.id'), nullable=True)
    generated_prompt = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    image_path = db.Column(db.String(500))
    comfyui_workflow = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'template_id': self.template_id,
            'generated_prompt': self.generated_prompt,
            'image_path': self.image_path,
            'comfyui_workflow': self.comfyui_workflow,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
