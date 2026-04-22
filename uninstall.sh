#!/bin/bash
set -e

echo "=== Удаление Prompt Manager ==="
echo ""

APP_DIR="/opt/prompt_manager"
USER="prompt"
DB_NAME="prompt_manager"
DB_USER="prompt_user"

if [ "$EUID" -ne 0 ]; then
    echo "Ошибка: запустите от root"
    exit 1
fi

echo "[1/5] Остановка сервисов..."
systemctl stop prompt_manager 2>/dev/null || true
systemctl disable prompt_manager 2>/dev/null || true
rm -f /etc/systemd/system/prompt_manager.service 2>/dev/null || true
systemctl daemon-reload

echo "[2/5] Удаление директорий..."
rm -rf $APP_DIR
rm -rf /var/lib/prompt_manager
rm -rf /var/backups/prompt_manager

echo "[3/5] Удаление пользователя..."
userdel $USER 2>/dev/null || true

echo "[4/5] Удаление PostgreSQL..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;" 2>/dev/null || true

# Очистка pg_hba.conf
PG_HBA="/etc/postgresql/15/main/pg_hba.conf"
if [ -f "$PG_HBA" ]; then
    sed -i "/prompt_user/d" "$PG_HBA"
    systemctl reload postgresql 2>/dev/null || true
fi

echo "[5/5] Удаление nginx конфига..."
rm -f /etc/nginx/sites-available/prompt_manager 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/prompt_manager 2>/dev/null || true
nginx -t 2>/dev/null || true
systemctl reload nginx 2>/dev/null || true

echo ""
echo "=== Удаление завершено ==="
echo ""
echo "Удалено:"
echo "  - $APP_DIR"
echo "  - /var/lib/prompt_manager"
echo "  - /var/backups/prompt_manager"
echo "  - Пользователь $USER"
echo "  - База данных $DB_NAME"
echo "  - PostgreSQL пользователь $DB_USER"
echo "  - systemd сервис"
echo "  - nginx конфиг"