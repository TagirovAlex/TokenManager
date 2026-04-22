import os
import hashlib


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


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
        return f"{object_id}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}.{ext}"
    
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


from datetime import datetime