# Panduan Migrasi SQLite → PostgreSQL (Production-Ready)

> Target: deploy ke production skala perusahaan.
> Bahasa: santai, detail, plus alasan kenapa tiap langkah penting.

---

## Daftar Isi

1. [Kenapa PostgreSQL, bukan SQLite lagi?](#1-kenapa-postgresql)
2. [Strategi Migrasi: Fresh Install vs Migrate Data](#2-strategi-migrasi)
3. [Step 1 — Install PostgreSQL di Lokal](#step-1--install-postgresql-di-lokal)
4. [Step 2 — Bikin Database & User di PostgreSQL](#step-2--bikin-database--user)
5. [Step 3 — Update `settings.py` dan `.env`](#step-3--update-settingspy-dan-env)
6. [Step 4 — Migrasi Data dari SQLite ke PostgreSQL](#step-4--migrasi-data-dari-sqlite-ke-postgresql)
7. [Step 5 — Verifikasi & Test](#step-5--verifikasi--test)
8. [Step 6 — Production Deployment Tips](#step-6--production-deployment-tips)
9. [Backup & Disaster Recovery](#backup--disaster-recovery)
10. [FAQ & Troubleshooting](#faq--troubleshooting)

---

## 1. Kenapa PostgreSQL?

### SQLite vs PostgreSQL — ringkas

| Aspek | SQLite | PostgreSQL |
|-------|--------|------------|
| Tipe | File-based (satu file `.db`) | Server-based (daemon) |
| Concurrency | 1 writer sekaligus, locked | Multi-writer, MVCC |
| Skala | <100 user concurrent | ribuan user concurrent |
| Data types | Basic (TEXT, INTEGER, REAL, BLOB) | Lengkap (JSON, Array, UUID, Range, Full-text search) |
| Backup hot | Nggak bisa — harus copy file saat idle | Bisa (pg_dump online, streaming replication) |
| User & permission | Nggak ada | Lengkap (role, grant, row-level security) |
| Extension | Minim | Banyak (PostGIS, pg_trgm, pgvector, dll.) |
| Deploy | Cuma drop file | Perlu setup server/managed service |

### Alasan buat project kamu

**1. Concurrent write.** Project kamu punya tiga role (master, annotator, reviewer) yang bisa nulis bersamaan — anotasi baru, komentar issue, update status. SQLite nge-lock seluruh file pas ada yang nulis, jadi user lain nunggu. Di production dengan puluhan annotator kerja barengan, ini bakal jadi bottleneck besar.

**2. Data integrity.** PostgreSQL punya constraint lebih ketat (`NOT NULL`, `CHECK`, foreign key yang bener-bener di-enforce, transaction isolation level yang bisa dipilih). Buat data anotasi yang penting, ini worth it.

**3. Backup tanpa downtime.** `pg_dump` bisa jalan saat DB lagi dipake user. SQLite? Harus matiin app atau risk file corrupt.

**4. Tooling.** pgAdmin, DBeaver, Metabase — semua jalan di Postgres. SQLite tools terbatas.

**5. Managed cloud.** AWS RDS, Google Cloud SQL, Azure Database, Supabase, Neon — semua offer managed PostgreSQL. SQLite nggak ada yang hosted (karena nggak masuk akal).

### Kapan SQLite masih OK?

- Dev lokal (tapi lebih bagus samain dengan prod = Postgres, hindari bug "jalan di lokal, gagal di prod")
- Aplikasi single-user (desktop app, mobile app cache)
- Read-heavy dengan traffic kecil (blog personal)

Untuk "sekelas perusahaan" seperti kata kamu — **PostgreSQL adalah no-brainer**.

---

## 2. Strategi Migrasi

Kamu punya dua opsi:

### Opsi A — Fresh Install (Recommended buat kamu)

Bikin DB kosong baru di Postgres, jalanin `migrate`, lalu bikin seed data atau import ulang dataset. **Cocok kalau:**
- Data di SQLite sekarang mostly dummy / testing
- Struktur model masih berubah-ubah (kayak bug #1 & #2 di laporan sebelumnya)
- Kamu mau start clean tanpa bawa "hutang data"

### Opsi B — Migrate Data (kalau datanya penting)

Export data SQLite → import ke Postgres. Method yang paling aman di Django: `dumpdata` + `loaddata`. **Cocok kalau:**
- Ada data real yang udah dipake annotator
- Nggak mau ngetik ulang dataset

**Saran saya:** Start dengan Opsi A. Fix dulu bug class duplikat `Annotation` (dari laporan sebelumnya), baru deploy. Kalau ada data SQLite penting, pisahkan dulu ke CSV, import manual.

Saya tetap kasih cara Opsi B di Step 4, buat jaga-jaga.

---

## Step 1 — Install PostgreSQL di Lokal

### macOS (paling umum buat developer)

**Opsi A — Homebrew (paling gampang):**
```bash
brew install postgresql@16
brew services start postgresql@16

# Cek jalan atau belum
psql --version
```

**Opsi B — Postgres.app (GUI, plug-and-play):**
Download dari https://postgresapp.com/, drag ke Applications, klik "Initialize". Sudah.

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl enable --now postgresql

# Cek status
sudo systemctl status postgresql
```

### Windows

Download installer dari https://www.postgresql.org/download/windows/. Jalan wizard, inget password yang kamu set buat user `postgres`. Port default 5432.

### Docker (paling clean, recommended buat tim)

```bash
docker run --name anotasi-postgres \
  -e POSTGRES_USER=anotasi_user \
  -e POSTGRES_PASSWORD=password_yang_kuat \
  -e POSTGRES_DB=anotasi_db \
  -p 5432:5432 \
  -v anotasi_pgdata:/var/lib/postgresql/data \
  -d postgres:16
```

**Kenapa Docker?**
- Environment sama di semua developer — hilang masalah "di laptop gue jalan, di laptop lu nggak"
- Gampang di-reset kalau DB-nya kotor (`docker rm`)
- Ready-to-go ke production (Kubernetes, ECS, dll.)

---

## Step 2 — Bikin Database & User

Jangan pakai user `postgres` langsung untuk aplikasi — ini user super-admin, kalau bocor kredensialnya, semua DB di server kena. Bikin user khusus.

### Konek ke psql

```bash
# macOS Homebrew / Linux
sudo -u postgres psql
# atau
psql postgres

# Docker (dari host)
docker exec -it anotasi-postgres psql -U anotasi_user -d anotasi_db
```

### Bikin DB + User + Grant (skip kalau pakai Docker, udah auto dibikin)

Di dalam psql:

```sql
-- 1. Bikin user (role) untuk aplikasi
CREATE USER anotasi_user WITH PASSWORD 'ganti_ini_dengan_password_kuat';

-- 2. Bikin database
CREATE DATABASE anotasi_db OWNER anotasi_user;

-- 3. Kasih privilege
GRANT ALL PRIVILEGES ON DATABASE anotasi_db TO anotasi_user;

-- 4. (Postgres 15+) kasih akses ke schema public
\c anotasi_db
GRANT ALL ON SCHEMA public TO anotasi_user;

-- 5. Keluar
\q
```

**Kenapa pisah user?**
- Principle of **least privilege** — user app cuma bisa ngutak-ngatik DB dia sendiri
- Kalau kredensial app bocor (misal kena SQL injection), attacker nggak bisa drop DB lain
- Bisa buat multiple user: `anotasi_readonly_user` buat reporting, `anotasi_user` buat app, dsb.

### Test konek

```bash
psql -U anotasi_user -d anotasi_db -h localhost
# Masukin password
# Kalau masuk, sukses
```

---

## Step 3 — Update `settings.py` dan `.env`

### A. Buat file `.env` di root project

Taro di folder `Anotasi-image_X15-clean/` (sejajar sama `manage.py` folder parent-nya).

```env
# ===== Django =====
DJANGO_SECRET_KEY=ganti_dengan_random_string_panjang_minimal_50_char
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ===== Database (PostgreSQL) =====
DB_ENGINE=django.db.backends.postgresql
DB_NAME=anotasi_db
DB_USER=anotasi_user
DB_PASSWORD=ganti_ini_dengan_password_kuat
DB_HOST=localhost
DB_PORT=5432

# ===== Google OAuth (kalau dipake) =====
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# ===== Email =====
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# ===== AI Service =====
AI_API_URL=https://pursue-various-engineer-corporate.trycloudflare.com/api/proses-gambar/
```

**Generate SECRET_KEY random:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Wajib:** tambahin `.env` ke `.gitignore` biar nggak ke-commit. Jangan pernah push credential ke Git!

### B. Update `Anotasi_Image/settings.py`

Ganti bagian `DATABASES` (baris 75–81 di file aktif) jadi:

```python
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
        'CONN_MAX_AGE': 600,  # koneksi reuse 10 menit (kurangi overhead connect)
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# Kalau butuh fallback SQLite untuk development lokal tanpa Postgres:
if os.getenv('USE_SQLITE', 'False').lower() == 'true':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
```

**Penjelasan tiap opsi:**

| Opsi | Apa gunanya | Kenapa penting |
|------|-------------|----------------|
| `CONN_MAX_AGE: 600` | Django pakai ulang koneksi DB selama 10 menit sebelum tutup | Bikin-tutup koneksi TCP mahal (5-50ms tiap request). Di production, reuse = throughput naik 2–5x |
| `connect_timeout: 10` | Kalau DB nggak respon dalam 10 detik, error | Biar request nggak nge-hang selamanya saat DB down |
| Fallback `USE_SQLITE` | Optional dev di laptop tanpa Postgres | Praktis kalau lagi di jalan, nggak butuh setup server |

### C. Pastikan `psycopg2` terinstall

Udah ada di requirements.txt (`psycopg2-binary==2.9.10`). Tinggal install:

```bash
pip install -r requirements.txt
```

**Catatan:** `psycopg2-binary` vs `psycopg2`:
- `psycopg2-binary` = precompiled, gampang install, cocok buat dev
- `psycopg2` (non-binary) = compile dari source, butuh libpq-dev, tapi lebih optimal di production

Untuk project real production, banyak tim pakai `psycopg[binary,pool]` (v3) yang lebih baru:
```
psycopg[binary,pool]==3.2.1
```
Tapi karena kamu udah pakai v2, stay dulu sampai project stabil.

---

## Step 4 — Migrasi Data dari SQLite ke PostgreSQL

### Skenario A: Fresh Install (rekomendasi)

```bash
# Pastikan settings udah di-update & .env udah diisi
cd Anotasi_Image

# Cek konek ke Postgres
python manage.py dbshell
# Kalau masuk ke prompt psql, sukses. Ketik \q buat keluar.

# Jalanin migration (bikin semua tabel)
python manage.py migrate

# Buat superuser
python manage.py createsuperuser

# Done! Test runserver
python manage.py runserver
```

### Skenario B: Migrate Data Lama (pakai dumpdata → loaddata)

**Step B.1. Backup SQLite dulu (wajib!)**
```bash
cp db.sqlite3 db.sqlite3.backup
```

**Step B.2. Export data dari SQLite**

Masih pake settings yang lama (SQLite). Kasih env `USE_SQLITE=true` atau sementara pakai settings SQLite:

```bash
# Export data ke JSON
python manage.py dumpdata \
  --natural-foreign \
  --natural-primary \
  --exclude contenttypes \
  --exclude auth.permission \
  --indent 2 \
  --output data_backup.json
```

**Kenapa exclude `contenttypes` dan `auth.permission`?**
Kedua ini akan dibuat ulang otomatis pas `migrate`. Kalau ikut di-export, bakal ada conflict primary key pas import.

**Kenapa `--natural-foreign --natural-primary`?**
Pakai "natural key" (nama unik) alih-alih integer ID. Jadi relasi antar tabel nggak break kalau ID shift saat import.

**Step B.3. Switch ke Postgres**

Update `.env` (`USE_SQLITE=false` atau unset).

**Step B.4. Buat schema di Postgres**
```bash
python manage.py migrate
```

**Step B.5. Import data**
```bash
python manage.py loaddata data_backup.json
```

**Step B.6. Reset sequence (penting!)**

SQLite pakai ROWID, Postgres pakai SEQUENCE. Setelah loaddata, kadang sequence nggak sync — insert baru bakal error "duplicate key". Reset:

```bash
python manage.py sqlsequencereset master annotator reviewer | python manage.py dbshell
```

### Skenario C: Tool Pihak Ketiga (pgloader)

Kalau mau lebih advanced, `pgloader` bisa langsung pipe SQLite → Postgres:

```bash
# macOS
brew install pgloader

# Ubuntu
sudo apt install pgloader

# Jalanin
pgloader sqlite:///path/to/db.sqlite3 \
  postgresql://anotasi_user:password@localhost/anotasi_db
```

Untung: cepet dan bisa handle type mapping yang tricky.
Rugi: kadang harus manual fix beberapa tabel setelahnya.

**Saya saranin Skenario A (fresh) untuk project kamu** — karena lagi fase active development & ada bug struktural yang perlu di-fix.

---

## Step 5 — Verifikasi & Test

Setelah migrasi, cek hal-hal ini:

### A. Konek DB
```bash
python manage.py dbshell
```
Kalau masuk ke `psql`, sukses.

### B. Tabel udah kebikin

Di dalam psql:
```sql
\dt
-- Harusnya muncul: master_customuser, master_jobprofile, master_jobimage,
-- master_annotation, master_notification, dll.
```

### C. Jalanin test

```bash
python manage.py test
```

Kalau ada error, kemungkinan:
- Model pakai feature SQLite-specific (jarang di Django ORM)
- Migration conflict (bug #1 dari laporan sebelumnya bakal kena di sini!)

### D. Runserver & manual test
```bash
python manage.py runserver
```

Tes skenario end-to-end:
1. Signup annotator baru
2. Login sebagai master, bikin job, assign ke annotator
3. Login annotator, buka job, anotasi gambar
4. Login reviewer, review hasil
5. Cek data di psql: `SELECT * FROM master_annotation LIMIT 5;`

### E. Cek connection pool aktif

Di psql:
```sql
SELECT
  state,
  COUNT(*)
FROM pg_stat_activity
WHERE datname = 'anotasi_db'
GROUP BY state;
```

Harus ada `idle` (koneksi di-cache oleh CONN_MAX_AGE) dan `active` (lagi dipake).

---

## Step 6 — Production Deployment Tips

Saat kamu actually deploy ke production, ada beberapa hal wajib:

### 1. DB Managed (jangan self-host kalau skala kecil)

Opsi bagus:
- **AWS RDS PostgreSQL** — mature, banyak fitur, paling populer enterprise
- **Google Cloud SQL** — integrasi GKE bagus
- **Azure Database for PostgreSQL** — pilih kalau ekosistem Microsoft
- **Supabase** — gratis sampai 500 MB, cocok startup
- **Neon** — serverless Postgres, scale to zero, murah
- **Railway / Render** — simple PaaS, satu-klik setup

**Keuntungan managed:** backup otomatis, patching, high availability, monitoring. Harga mulai $15-30/bulan untuk tier kecil.

### 2. Connection Pooling (wajib di production)

Django `CONN_MAX_AGE` hanya pool per-process. Kalau pakai gunicorn dengan 8 worker = 8 koneksi minimum per request. Scale to 100 RPS dengan 10 instance = 800 koneksi simultan. Postgres default max 100 — bakal kena limit.

Solusi:
- **PgBouncer** — di depan Postgres, pool koneksi. Standar industri.
- **Supabase/Neon** — udah built-in connection pooler.
- **Django package `django-db-connection-pool`** — in-process pooling.

### 3. Environment-specific settings

Pisahkan settings:
```
Anotasi_Image/
├── settings/
│   ├── __init__.py
│   ├── base.py        # common config
│   ├── development.py # extend base, DEBUG=True, SQLite optional
│   ├── production.py  # extend base, DEBUG=False, security settings
│   └── testing.py     # untuk CI/CD
```

Set `DJANGO_SETTINGS_MODULE=Anotasi_Image.settings.production` saat deploy.

### 4. Security untuk production

Di `production.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',  # WAJIB production!
            'connect_timeout': 10,
        },
    }
}
```

**Kenapa `sslmode=require`?**
Tanpa SSL, koneksi dari app server ke DB bisa di-sniff di network. Semua managed Postgres support SSL — gratis, tinggal enable.

### 5. Monitoring

Install di production:
- **django-debug-toolbar** (dev only)
- **Sentry** — error tracking
- **New Relic / Datadog** — APM, query slow log
- **pgbadger** — analisis Postgres log

### 6. Redis untuk cache & session

Di production, pindah session dari DB ke Redis:
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
    }
}
```

**Kenapa?** Setiap request hit DB buat validasi session = boros. Redis in-memory, 100x lebih cepet.

### 7. File storage (media)

SQLite/local filesystem buat `MEDIA_ROOT` nggak scale. Kalau deploy ke multi-instance (load balancer), tiap instance punya filesystem sendiri — upload di server 1 nggak kelihatan di server 2.

Pindah ke S3-compatible:
```bash
pip install django-storages[boto3]
```

```python
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'anotasi-media'
AWS_S3_REGION_NAME = 'ap-southeast-1'
```

Alternatif murah: Cloudflare R2, Backblaze B2, MinIO (self-host).

---

## Backup & Disaster Recovery

### Backup otomatis harian

Script `backup_pg.sh`:
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups
DB_NAME=anotasi_db

pg_dump -U anotasi_user -h localhost \
  -F c \
  -f $BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump \
  $DB_NAME

# Hapus backup >30 hari
find $BACKUP_DIR -name "*.dump" -mtime +30 -delete

# Upload ke S3 (optional)
aws s3 cp $BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump \
  s3://anotasi-backups/
```

Jadwalkan via cron:
```
0 2 * * * /path/to/backup_pg.sh
```

### Restore

```bash
pg_restore -U anotasi_user -d anotasi_db \
  --clean --if-exists \
  /backups/anotasi_db_20260418_020000.dump
```

### Testing backup (wajib!)

Setiap bulan, restore backup ke staging DB. Kalau nggak pernah di-test, backup-nya kayak parasut yang nggak pernah dicek — percuma saat butuh.

---

## FAQ & Troubleshooting

### Q: "psycopg2 error: Library not loaded" di macOS
A: Install `libpq`:
```bash
brew install libpq
echo 'export PATH="/opt/homebrew/opt/libpq/bin:$PATH"' >> ~/.zshrc
```

### Q: "role 'anotasi_user' does not exist"
A: Kamu belum bikin user di Postgres. Balik ke Step 2.

### Q: "duplicate key value violates unique constraint"
A: Sequence nggak sync. Jalanin:
```bash
python manage.py sqlsequencereset master | python manage.py dbshell
```

### Q: Aplikasi lambat banget setelah pindah Postgres
A: Kemungkinan:
1. Nggak ada index di field yang sering di-filter. Cek di `models.py` — pastikan pakai `db_index=True` atau `Meta.indexes`.
2. N+1 query. Pakai `select_related()` dan `prefetch_related()`.
3. Nggak pakai CONN_MAX_AGE.

### Q: Field `JSONField` yang di SQLite disimpan sebagai TEXT, pas migrate ke Postgres jadi rusak
A: Setelah migrate, jalanin `python manage.py shell` dan check beberapa row manual. Kalau perlu, tulis data migration manual.

### Q: Kapan pake `psycopg3` vs `psycopg2`?
A: Tunggu sampai project stable. psycopg3 lebih cepet & async-ready, tapi breaking changes. Upgrade saat ada jadwal maintenance.

---

## Checklist Sebelum Deploy Production

- [ ] `.env` udah di `.gitignore`
- [ ] `SECRET_KEY` unique per environment
- [ ] `DEBUG=False` di production
- [ ] `ALLOWED_HOSTS` tidak pakai `*`
- [ ] DB pakai SSL (`sslmode=require`)
- [ ] `CONN_MAX_AGE` dikonfigurasi
- [ ] Connection pooling (PgBouncer) active
- [ ] Backup otomatis berjalan & di-test restore
- [ ] Monitoring (Sentry/Datadog) terpasang
- [ ] Static files dilayani via CDN atau Whitenoise
- [ ] Media files di object storage (S3/R2)
- [ ] Rate limiting di web server (Nginx/Cloudflare)
- [ ] HTTPS aktif (Let's Encrypt / Cloudflare)
- [ ] Database user tidak pakai `postgres` (superuser)

---

## Urutan Kerja Saat Ini

Berdasarkan state project kamu sekarang:

1. ✅ Install PostgreSQL lokal (Step 1)
2. ✅ Bikin DB & user (Step 2)
3. ⚠️ **Fix dulu bug duplicate class `Annotation`** (dari laporan sebelumnya) sebelum migrate — kalau nggak, migration di Postgres bakal gagal.
4. ✅ Update settings & .env (Step 3)
5. ✅ Fresh migrate (Skenario A di Step 4)
6. ✅ Test lokal dengan Postgres
7. ⏳ Deploy ke staging (pakai Railway / Render dulu biar cepat)
8. ⏳ Hardening production (Step 6)

**Estimasi waktu:** 2–4 jam buat semua step 1–6 kalau nggak ada drama.

Kalau stuck di step manapun, lempar error-nya ke chat — saya bantu debug.

— Good luck deploy!
