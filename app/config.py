import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
        'postgresql://prompt_user:password@localhost:5432/prompt_manager')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))
    SERVER_DEBUG = os.getenv('SERVER_DEBUG', 'True').lower() == 'true'
    
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', '/var/lib/prompt_manager/uploads')
    MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 10485760))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    COMFYUI_HOST = os.getenv('COMFYUI_HOST', 'http://localhost:8188')
    COMFYUI_API_KEY = os.getenv('COMFYUI_API_KEY', '')
    COMFYUI_TIMEOUT = int(os.getenv('COMFYUI_TIMEOUT', 30))
    
    BACKUP_DIR = os.getenv('BACKUP_DIR', '/var/backups/prompt_manager')
    BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
    
    DEFAULT_IMAGE_WIDTH = 512
    DEFAULT_IMAGE_HEIGHT = 512
    DEFAULT_SEEDS = 1
    DEFAULT_STEPS = 20
    DEFAULT_CFG = 8
    DEFAULT_SAMPLER = 'euler'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
