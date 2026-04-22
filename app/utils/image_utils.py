import os
import hashlib
from datetime import datetime
from PIL import Image


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
TARGET_SIZE = 512


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def generate_image_filename(original_filename, object_id=None):
    ext = get_extension(original_filename)
    if not ext:
        ext = 'png'
    
    if object_id:
        return f"{object_id}.{ext}"
    
    return f"{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:16]}.{ext}"


def get_image_path(upload_dir, filename):
    return os.path.join(upload_dir, filename)


def ensure_upload_dir(upload_dir):
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)


def delete_image(image_path):
    if image_path and os.path.exists(image_path):
        os.remove(image_path)
        return True
    return False


def process_and_save_image(file, upload_dir, filename):
    ensure_upload_dir(upload_dir)
    
    img = Image.open(file)
    
    width, height = img.size
    min_dim = min(width, height)
    
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    
    img = img.crop((left, top, right, bottom))
    
    img = img.resize((TARGET_SIZE, TARGET_SIZE), Image.Resampling.LANCZOS)
    
    ext = get_extension(filename)
    if not ext:
        ext = 'png'
    
    output_path = os.path.join(upload_dir, filename)
    
    if ext.lower() in ['jpg', 'jpeg']:
        img.save(output_path, 'JPEG', quality=95)
    else:
        img.save(output_path)
    
    return filename