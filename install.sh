#!/bin/bash
set -e

echo "=== Установка Prompt Manager ==="
echo ""

APP_DIR="/opt/prompt_manager"
USER="prompt"
GROUP="prompt"
DB_NAME="prompt_manager"
DB_USER="prompt_user"
DB_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)

if [ "$EUID" -ne 0 ]; then
    echo "Ошибка: запустите от root"
    exit 1
fi

echo "[1/8] Обновление системы..."
apt update && apt upgrade -y

echo "[2/8] Установка зависимостей..."
apt install -y python3.11 python3.11-venv python3-pip postgresql nginx git openssl libpq-dev

echo "[3/8] Настройка PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql

su - postgres -c "psql -c \"CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';\"" 2>/dev/null || true
su - postgres -c "psql -c \"CREATE DATABASE $DB_NAME OWNER $DB_USER;\"" 2>/dev/null || true
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;\"" 2>/dev/null || true

echo "[4/8] Создание пользователя приложения..."
useradd -r -s /bin/bash $USER 2>/dev/null || true

echo "[5/8] Создание директорий..."
mkdir -p $APP_DIR
mkdir -p /var/lib/prompt_manager/uploads
mkdir -p /var/backups/prompt_manager
chown -R $USER:$GROUP $APP_DIR
chown -R $USER:$GROUP /var/lib/prompt_manager
chown -R $USER:$GROUP /var/backups/prompt_manager

echo "[6/8] Настройка приложения..."
cd $APP_DIR
cp -r . /opt/prompt_manager/

python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install --no-cache-dir -r requirements.txt

cat > .env << EOF
SECRET_KEY=$(openssl rand -base64 32)
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
SERVER_HOST=127.0.0.1
SERVER_PORT=5000
SERVER_DEBUG=False
UPLOAD_DIR=/var/lib/prompt_manager/uploads
BACKUP_DIR=/var/backups/prompt_manager
COMFYUI_HOST=http://localhost:8188
EOF

chown -R $USER:$GROUP $APP_DIR/.env

echo "[7/8] Настройка systemd..."
cp deploy/prompt_manager.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable prompt_manager

echo "[8/8] Запуск..."
systemctl start prompt_manager

echo ""
echo "=== Установка завершена ==="
echo ""
echo "URL: http://localhost:5000"
echo "Директория: $APP_DIR"
echo "Логи: journalctl -u prompt_manager -f"
echo ""
echo "Для настройки nginx добавьте конфиг из deploy/nginx.conf"
