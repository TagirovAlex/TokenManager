import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 
        'postgresql://prompt_user:password@localhost:5432/prompt_manager')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['SERVER_HOST'] = os.getenv('SERVER_HOST', '0.0.0.0')
    app.config['SERVER_PORT'] = int(os.getenv('SERVER_PORT', 5000))
    app.config['SERVER_DEBUG'] = os.getenv('SERVER_DEBUG', 'True').lower() == 'true'
    
    app.config['UPLOAD_DIR'] = os.getenv('UPLOAD_DIR', '/var/lib/prompt_manager/uploads')
    app.config['MAX_IMAGE_SIZE'] = int(os.getenv('MAX_IMAGE_SIZE', 10485760))
    
    app.config['COMFYUI_HOST'] = os.getenv('COMFYUI_HOST', 'http://localhost:8188')
    app.config['COMFYUI_API_KEY'] = os.getenv('COMFYUI_API_KEY', '')
    app.config['COMFYUI_TIMEOUT'] = int(os.getenv('COMFYUI_TIMEOUT', 30))
    
    app.config['BACKUP_DIR'] = os.getenv('BACKUP_DIR', '/var/backups/prompt_manager')
    app.config['BACKUP_RETENTION_DAYS'] = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
    
    app.config['DEFAULT_IMAGE_WIDTH'] = int(os.getenv('DEFAULT_IMAGE_WIDTH', 512))
    app.config['DEFAULT_IMAGE_HEIGHT'] = int(os.getenv('DEFAULT_IMAGE_HEIGHT', 512))
    app.config['DEFAULT_SEEDS'] = int(os.getenv('DEFAULT_SEEDS', 1))
    app.config['DEFAULT_STEPS'] = int(os.getenv('DEFAULT_STEPS', 20))
    app.config['DEFAULT_CFG'] = int(os.getenv('DEFAULT_CFG', 8))
    app.config['DEFAULT_SAMPLER'] = os.getenv('DEFAULT_SAMPLER', 'euler')
    
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400
    
    db.init_app(app)
    
    from app.routes import web, api, auth
    app.register_blueprint(web)
    app.register_blueprint(api)
    app.register_blueprint(auth)
    
    with app.app_context():
        db.create_all()
    
    return app