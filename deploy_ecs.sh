#!/bin/bash

# =====================================================
# Skrip Deployment / Update BI Engine ke Ubuntu ECS
# Capstone Project - Versi 2.0 (Update dari Repo Baru)
# =====================================================

set -e  # Hentikan jika ada perintah yang gagal

APP_DIR=$(pwd)
SERVICE_NAME="bi-engine"
VENV_DIR="$APP_DIR/venv"
PYTHON_BIN="$VENV_DIR/bin/python"
UVICORN_BIN="$VENV_DIR/bin/uvicorn"

echo "======================================================="
echo " BI Engine - Deployment & Update Script"
echo " Working Directory: $APP_DIR"
echo "======================================================="

# 1. Update sistem
echo ""
echo "[1/7] Memperbarui sistem Ubuntu dan menginstal dependensi dasar..."
sudo apt update
sudo apt install python3-pip python3-venv git -y

# 2. Stop service lama jika sedang berjalan
echo ""
echo "[2/7] Menghentikan service lama (jika ada)..."
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    sudo systemctl stop $SERVICE_NAME
    echo "  -> Service '$SERVICE_NAME' dihentikan."
else
    echo "  -> Service '$SERVICE_NAME' tidak sedang berjalan, lanjut..."
fi

# 3. Setup atau perbarui Virtual Environment
echo ""
echo "[3/7] Menyiapkan Virtual Environment Python..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv venv
    echo "  -> Virtualenv baru dibuat."
else
    echo "  -> Virtualenv sudah ada, digunakan kembali."
fi
source venv/bin/activate

# 4. Install / Update semua library Python
echo ""
echo "[4/7] Menginstal/Memperbarui library Python dari requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Membuat direktori cache
echo ""
echo "[5/7] Menyiapkan direktori cache..."
mkdir -p cache
chmod 777 cache

# 6. Menulis ulang file service Systemd
echo ""
echo "[6/7] Mengonfigurasi ulang Systemd Service..."
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

sudo bash -c "cat > $SERVICE_FILE" << EOL
[Unit]
Description=BI Engine FastAPI Server (Capstone v2)
After=network.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$UVICORN_BIN api_server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

echo "  -> File service ditulis ke $SERVICE_FILE"

# 7. Reload dan restart service
echo ""
echo "[7/7] Memulai ulang API Server..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

sleep 3

# Verifikasi akhir
echo ""
echo "======================================================="
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "  ✅ Deployment BERHASIL! API sedang berjalan."
    echo "  Akses API di: http://$(curl -s ifconfig.me):8000"
    echo "  Dokumentasi : http://$(curl -s ifconfig.me):8000/docs"
else
    echo "  ❌ Deployment GAGAL. Cek log dengan perintah:"
    echo "  sudo journalctl -u $SERVICE_NAME -n 50 --no-pager"
fi
echo "======================================================="
