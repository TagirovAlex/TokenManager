#!/bin/bash
set -e

echo "=== Установка Prompt Manager ==="
echo ""

APP_DIR="/opt/prompt_manager"
USER="prompt"
GROUP="prompt"
DB_NAME="prompt_manager"
DB_USER="prompt_user"

# Читаем настройки БД из .env ТЕКУЩЕЙ дире��тории (где запускается скрипт)
CURRENT_DIR=$(pwd)
if [ -f "$CURRENT_DIR/.env" ]; then
    source "$CURRENT_DIR/.env"
fi
# Если не задан пароль - генерируем
if [ -z "$DB_PASS" ]; then
    DB_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
fi

if [ "$EUID" -ne 0 ]; then
    echo "Ошибка: запустите от root"
    exit 1
fi

echo "Настройки БД: пользователь=$DB_USER, пароль=${DB_PASS:0:8}..."

echo "[1/8] Обновление системы..."
apt update && apt upgrade -y

echo "[2/8] Установка зависимостей..."
apt install -y python3.11 python3.11-venv python3-pip postgresql nginx git openssl libpq-dev

echo "[3/8] Настройка PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql

# Находим pg_hba.conf - может быть в разных версиях
PG_VERSION=$(ls -1 /etc/postgresql/ | sort -V | tail -1)
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
echo "Используем pg_hba.conf: $PG_HBA"

# Экранируем пароль для SQL
DB_PASS_SQL=$(echo "$DB_PASS" | sed "s/'/''/g")

# Удаляем старого пользователя и создаём заново
su - postgres -c "psql -c \"DROP USER IF EXISTS $DB_USER;\"" 2>/dev/null || true
su - postgres -c "psql -c \"DROP DATABASE IF EXISTS $DB_NAME;\"" 2>/dev/null || true
su - postgres -c "psql -c \"CREATE USER $DB_USER WITH PASSWORD '$DB_PASS_SQL';\"" 2>/dev/null || true
su - postgres -c "psql -c \"CREATE DATABASE $DB_NAME OWNER $DB_USER;\"" 2>/dev/null || true
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;\"" 2>/dev/null || true

# Полностью перезаписываем pg_hba.conf - ВЕСЬ ФАЙЛ
if [ -f "$PG_HBA" ]; then
    cat > "$PG_HBA" << 'PGHBA'
# PostgreSQL Client Authentication Configuration File
# Local connections - trust (no password)
local   all             all                                         trust
# IPv4 local connections
host    all             all             127.0.0.1/32              trust
# IPv6 local connections
host    all             all             ::1/128                       trust
PGHBA
    # Меняем права и перезапускаем
    chmod 640 "$PG_HBA"
    chown postgres:postgres "$PG_HBA"
    systemctl reload postgresql
fi

# Тестируем подключение через unix socket
echo "Проверка подключения к БД..."
su - postgres -c "psql -d $DB_NAME -c 'SELECT 1;'" && echo "Подключение успешно!" || echo "ОШИБКА подключения!"

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
# Всегда клонируем/обновляем проект
if [ ! -f "$APP_DIR/run.py" ]; then
    rm -rf $APP_DIR
    git clone https://github.com/TagirovAlex/TokenManager.git $APP_DIR
else
    cd $APP_DIR && git pull origin master
fi

# Используем .env из текущей директории, перезаписываем в APP_DIR
# Сначала проверяем текущую директорию
CURRENT_DIR=$(pwd)
if [ -f "$CURRENT_DIR/.env" ]; then
    cp "$CURRENT_DIR/.env" "$APP_DIR/.env"
    echo "Использован .env из текущей директории"
elif [ ! -f "$APP_DIR/.env" ]; then
    # Создаём новый .env если нет
    if [ -z "$DB_PASS" ]; then
        DB_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
    fi
    cat > $APP_DIR/.env << EOF
SECRET_KEY=$(openssl rand -base64 32)
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost:5432/$DB_NAME
SERVER_HOST=127.0.0.1
SERVER_PORT=5000
SERVER_DEBUG=False
UPLOAD_DIR=/var/lib/prompt_manager/uploads
BACKUP_DIR=/var/backups/prompt_manager
COMFYUI_HOST=http://localhost:8188
EOF
fi

python3.11 -m venv $APP_DIR/venv
source $APP_DIR/venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install --no-cache-dir -r $APP_DIR/requirements.txt

chown -R $USER:$GROUP $APP_DIR

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
