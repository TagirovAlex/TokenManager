import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_KEY'] = os.getenv('SESSION_KEY', 'prompt-manager-sessions')
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 
        'postgresql://prompt_manager:prompt123@localhost:5432/prompt_manager')
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
    app.config['SESSION_FILE_DIR'] = os.getenv('SESSION_FILE_DIR', '/tmp/flask_sessions')
    app.config['SESSION_PERMANENT'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400
    
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    db.init_app(app)
    csrf.init_app(app)
    
    from app.routes import web, auth
    app.register_blueprint(web)
    app.register_blueprint(auth)
    
    upload_dir = os.getenv('UPLOAD_DIR', '/var/lib/prompt_manager/uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        from flask import send_from_directory
        return send_from_directory(upload_dir, filename)
    
    with app.app_context():
        db.create_all()
    
    return app