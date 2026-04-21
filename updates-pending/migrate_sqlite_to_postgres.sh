#!/bin/bash
# =============================================================
# migrate_sqlite_to_postgres.sh
# Script bantu migrasi data dari SQLite ke PostgreSQL.
# =============================================================
# Cara pakai:
#   1. chmod +x migrate_sqlite_to_postgres.sh
#   2. Jalanin dari folder yang ada manage.py
#   3. ./migrate_sqlite_to_postgres.sh
# =============================================================
# PREREQUISITES:
#   - PostgreSQL udah running
#   - DB & user udah dibikin (anotasi_db, anotasi_user)
#   - .env udah di-set untuk PostgreSQL
#   - Backup SQLite udah ada
# =============================================================

set -e  # Stop kalau ada error
set -u  # Error kalau ada variable yang belum di-set

echo "==================================================="
echo "  Migrasi SQLite -> PostgreSQL"
echo "==================================================="

# Warning
echo ""
echo "PERINGATAN:"
echo "  Script ini akan:"
echo "  1. Export data dari db.sqlite3 ke data_backup.json"
echo "  2. Jalanin migration di PostgreSQL (bikin schema)"
echo "  3. Import data_backup.json ke PostgreSQL"
echo "  4. Reset sequence"
echo ""
read -p "Lanjut? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Dibatalkan."
    exit 0
fi

# ==========================================================
# Step 1: Backup SQLite
# ==========================================================
echo ""
echo "[1/6] Backup db.sqlite3..."
if [ -f "db.sqlite3" ]; then
    cp db.sqlite3 "db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)"
    echo "  Backup dibuat: db.sqlite3.backup.*"
else
    echo "  WARNING: db.sqlite3 tidak ditemukan, skip backup."
fi

# ==========================================================
# Step 2: Export data ke JSON (pakai SQLite)
# ==========================================================
echo ""
echo "[2/6] Export data dari SQLite..."
export USE_SQLITE=true

python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude contenttypes \
    --exclude auth.permission \
    --exclude admin.logentry \
    --exclude sessions.session \
    --indent 2 \
    --output data_backup.json

if [ ! -s data_backup.json ]; then
    echo "  ERROR: Export gagal atau data kosong."
    exit 1
fi

BACKUP_SIZE=$(du -h data_backup.json | cut -f1)
echo "  Data di-export ke data_backup.json ($BACKUP_SIZE)"

# ==========================================================
# Step 3: Switch ke PostgreSQL
# ==========================================================
echo ""
echo "[3/6] Switch ke PostgreSQL..."
unset USE_SQLITE

# Test koneksi
if ! python manage.py check --database default 2>&1 | grep -q "System check identified no issues"; then
    echo "  Running system check..."
    python manage.py check --database default
fi

# ==========================================================
# Step 4: Jalanin migration di Postgres
# ==========================================================
echo ""
echo "[4/6] Jalanin migration di PostgreSQL..."
python manage.py migrate --noinput

# ==========================================================
# Step 5: Import data ke Postgres
# ==========================================================
echo ""
echo "[5/6] Import data ke PostgreSQL..."
python manage.py loaddata data_backup.json

# ==========================================================
# Step 6: Reset sequence (fix auto-increment)
# ==========================================================
echo ""
echo "[6/6] Reset sequence..."
for app in master annotator reviewer; do
    echo "  Resetting sequence untuk $app..."
    python manage.py sqlsequencereset $app | python manage.py dbshell || true
done

# ==========================================================
# Selesai
# ==========================================================
echo ""
echo "==================================================="
echo "  Migrasi SELESAI!"
echo "==================================================="
echo ""
echo "Next steps:"
echo "  1. Jalanin test: python manage.py test"
echo "  2. Test manual: python manage.py runserver"
echo "  3. Cek data di psql:"
echo "       python manage.py dbshell"
echo "       \\dt              (list tables)"
echo "       SELECT COUNT(*) FROM master_customuser;"
echo ""
echo "Backup:"
echo "  - SQLite: db.sqlite3.backup.*"
echo "  - JSON:   data_backup.json"
echo ""
