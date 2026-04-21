# ========================================
# Snippet untuk replace bagian DATABASES
# di Anotasi_Image/settings.py (yang aktif)
# ========================================
# Cara pakai:
# 1. Buka Anotasi_Image/settings.py
# 2. Cari baris 75-81 (yang mulai "# Database — SQLite")
# 3. Hapus blok DATABASES = {...} yang lama
# 4. Paste isi di bawah ini
# ========================================

# Database (PostgreSQL production-ready)
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'anotasi_db'),
        'USER': os.getenv('DB_USER', 'anotasi_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        # Production optimizations
        'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', '600')),  # 10 menit
        'OPTIONS': {
            'connect_timeout': 10,
            # Aktifkan SSL di production:
            # 'sslmode': os.getenv('DB_SSLMODE', 'prefer'),
        },
    }
}

# Fallback ke SQLite untuk development tanpa Postgres
# Set USE_SQLITE=true di .env kalau mau pakai
if os.getenv('USE_SQLITE', 'False').lower() == 'true':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

# ========================================
# Penjelasan tiap setting:
# ========================================
# CONN_MAX_AGE: berapa detik koneksi DB di-cache & dipake ulang.
#   - 0   = disable, bikin koneksi baru tiap request (boros)
#   - 600 = 10 menit (sweet spot untuk web app)
#   - None = persistent forever (hati-hati dengan idle timeout DB)
#
# connect_timeout: kalau DB nggak respond dalam 10 detik, error
#   alih-alih hang request selamanya.
#
# sslmode (production):
#   - 'disable'    = no SSL (jangan!)
#   - 'prefer'     = pake SSL kalau available (default Postgres)
#   - 'require'    = WAJIB SSL, error kalau nggak ada
#   - 'verify-ca'  = SSL + verify CA certificate
#   - 'verify-full'= SSL + verify CA + verify hostname (paling aman)
# ========================================
