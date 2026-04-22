import os
import shutil
import tarfile
import subprocess
import re
from datetime import datetime
from app import db
from app.models import Category, Object, Template, TemplateResult


def get_stats():
    return {
        'categories': Category.query.count(),
        'objects': Object.query.count(),
        'templates': Template.query.count(),
        'results': TemplateResult.query.count()
    }


def _ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def _validate_db_uri(uri):
    pattern = r'^postgresql://[^:]+:[^@]+@[^:]+:\d+/[a-zA-Z0-9_]+$'
    if not re.match(pattern, uri):
        raise ValueError('Invalid database URI format')
    return True


def create_backup(backup_dir, upload_dir, db_uri):
    _ensure_dir(backup_dir)
    
    _validate_db_uri(db_uri)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"prompt_manager_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    _ensure_dir(backup_path)
    
    if db_uri.startswith('postgresql://'):
        match = re.search(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', db_uri)
        if match:
            db_user, db_pass, db_host, db_port, db_name = match.groups()
            sql_file = os.path.join(backup_path, 'database.sql')
            env = os.environ.copy()
            env['PGPASSWORD'] = db_pass
            try:
                subprocess.run(
                    ['pg_dump', '-h', db_host, '-p', db_port, '-U', db_user, '-f', sql_file, db_name],
                    env=env,
                    check=True,
                    capture_output=True
                )
            except Exception as e:
                pass
    
    if upload_dir and os.path.exists(upload_dir):
        images_backup = os.path.join(backup_path, 'uploads.tar')
        with tarfile.open(images_backup, 'w') as tar:
            tar.add(upload_dir, arcname='uploads')
    
    backup_file = f"{backup_name}.tar.gz"
    full_backup_path = os.path.join(backup_dir, backup_file)
    with tarfile.open(full_backup_path, 'w:gz') as tar:
        tar.add(backup_path, arcname=backup_name)
    
    shutil.rmtree(backup_path)
    
    return {
        'message': 'Backup created',
        'backup_file': backup_file,
        'path': full_backup_path
    }


def list_backups(backup_dir):
    _ensure_dir(backup_dir)
    
    backups = []
    for f in os.listdir(backup_dir):
        if f.endswith('.tar.gz'):
            fpath = os.path.join(backup_dir, f)
            backups.append({
                'name': f,
                'size': os.path.getsize(fpath),
                'created': datetime.fromtimestamp(os.path.getctime(fpath)).isoformat()
            })
    return backups


def cleanup_unused_images(upload_dir):
    if not upload_dir or not os.path.exists(upload_dir):
        return {'message': 'No uploads directory', 'deleted': 0}
    
    query = TemplateResult.query.filter(TemplateResult.image_path.isnot(None))
    used_images = set()
    for r in query:
        if r.image_path:
            used_images.add(r.image_path)
    
    deleted_count = 0
    for root, dirs, files in os.walk(upload_dir):
        for f in files:
            fpath = os.path.join(root, f)
            rel_path = os.path.relpath(fpath, upload_dir)
            if rel_path not in used_images:
                os.remove(fpath)
                deleted_count += 1
    
    return {'deleted': deleted_count}