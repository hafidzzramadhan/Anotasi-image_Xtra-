# Laporan Debug & Belajar Fullstack — Anotasi Image

> **Bahasa:** Santai (nggak baku) — biar enak dibaca sambil ngoding.
> **Format:** Tiap bug dibahas dengan pola **Apa → Kenapa → Cara Fix → Pelajaran**.

---

## Ringkasan Cepat (TL;DR)

Saya nemu **10 masalah**, dari yang kritis sampai yang cuma "code smell". Urutan dari paling darurat:

| # | Bug | Level | File |
|---|-----|-------|------|
| 1 | Dua class `Annotation` di file yang sama | KRITIS | `master/models.py` |
| 2 | Field `image` vs `job_image` nggak konsisten antara create & filter | KRITIS | `annotator/views.py` |
| 3 | `ACCOUNT_SETTINGS` dibungkus dict (allauth nggak baca) | TINGGI | `Anotasi_Image/settings.py` |
| 4 | `AUTHENTICATION_BACKENDS` nggak include allauth backend | TINGGI | `Anotasi_Image/settings.py` |
| 5 | Dua `settings.py` berbeda di project | TINGGI | project structure |
| 6 | `DJANGO_SETTINGS_MODULE = 'settings'` (fragile) | MENENGAH | `manage.py` |
| 7 | Class `User` legacy yang nggak dipakai | MENENGAH | `master/models.py` |
| 8 | `ALLOWED_HOSTS` ada `"*"` hardcoded | MENENGAH | `Anotasi_Image/settings.py` |
| 9 | AI API URL hardcoded di views.py | MENENGAH | `annotator/views.py` |
| 10 | File debug/SQL/test bertebaran di root | RINGAN | project structure |

---

## Bug #1 — Dua Class `Annotation` di File yang Sama

### Apa masalahnya?

Di `master/models.py` ada **dua** class bernama `Annotation`:
- Yang pertama di baris **366–393** (versi simple: `image`, `label`, `x_min`, dst.)
- Yang kedua di baris **446–503** (versi lengkap: `job_image`, `segmentation`, `tool`, `annotator`, `status`, plus legacy fields `image`, `x_min` dll.)

### Kenapa ini masalah?

Python itu "last definition wins". Artinya class pertama **ditimpa diam-diam** sama yang kedua. Nggak ada error, nggak ada warning — tapi class pertama jadi sampah di otak developer. Kamu baca kode, ngerasa punya Annotation dengan struktur X, ternyata yang aktif malah struktur Y.

Selain itu, ini membingungkan Django. Migration 0001 udah dibuat berdasarkan class kedua (saya cek — field-nya cocok sama class baris 446). Jadi database sekarang ngikutin class kedua.

### Cara fix

Hapus class `Annotation` yang pertama (baris 366–393). Yang kedua udah punya semua field legacy (`image`, `label`, `x_min`, `y_min`, `x_max`, `y_max`, `is_auto_generated`, `created_by`) jadi nggak ada data yang hilang.

### Pelajaran fullstack

**Konsep: "Single Source of Truth" di ORM.** Satu entitas = satu class. Kalau perlu migrasi struktur, pakai Django migration (`makemigrations`) — jangan bikin class duplikat. Ini hukum ke-1 modeling database.

**Tip debugging:** Kalau kamu punya file panjang (>500 baris), coba `grep -n "class " master/models.py`. Kalau ada nama sama, langsung kelihatan.

---

## Bug #2 — Inkonsistensi Field `image` vs `job_image`

### Apa masalahnya?

Di `annotator/views.py`:

```python
# Baris 376 — INSERT pakai field `image`
Annotation.objects.create(
    image=image_obj,     # <-- field legacy
    label=label,
    ...
)

# Baris 426 — FILTER pakai field `job_image`
annotations = Annotation.objects.filter(
    job_image=image_obj  # <-- field baru
).values(...)
```

### Kenapa ini masalah?

`image` dan `job_image` itu dua **ForeignKey yang berbeda** (lihat class `Annotation` yang aktif di master/models.py). Saat kamu create dengan `image=X`, maka:
- `annotation.image_id` = X.id
- `annotation.job_image_id` = **NULL**

Pas kamu query `filter(job_image=X)`, Django cuma nyari row yang `job_image_id == X.id`. Karena yang disimpan ada di `image_id`, hasilnya **query kosong**. Data ada di DB, tapi nggak pernah muncul di UI. Mirip bug "ilmu ghaib" — kelihatannya kode jalan, tapi user ngeliat list kosong terus.

### Cara fix

Pilih SALAH SATU field dan konsisten. Saran: pakai `job_image` (nama yang lebih deskriptif karena FK-nya ke `JobImage`, bukan ke `Image`). Terus hapus field legacy `image` dari class `Annotation` dan buat migration baru.

Kalau mau aman (belum mau ubah DB), minimal samain:

```python
# Create & filter keduanya pakai job_image
Annotation.objects.create(job_image=image_obj, ...)
Annotation.objects.filter(job_image=image_obj)
```

### Pelajaran fullstack

**Konsep: Schema evolution.** Saat refactor nama field, harus dilakukan di **tiga tempat**:
1. Model (master/models.py)
2. Migration (bikin baru, jangan edit yang udah ada)
3. Semua views/queries yang pakai field itu

Cara paling aman: `git grep "image=" annotator/` dan `git grep "job_image=" annotator/` — cek dulu semua tempat yang kepengaruh sebelum commit.

---

## Bug #3 — `ACCOUNT_SETTINGS` Dict yang Nggak Dipakai

### Apa masalahnya?

Di `Anotasi_Image/settings.py` (yang aktif, di level atas) baris 122–127:

```python
ACCOUNT_SETTINGS = {
    'LOGIN_METHODS': {'email'},
    'EMAIL_REQUIRED': True,
    'UNIQUE_EMAIL': True,
    'USERNAME_REQUIRED': False,
}
```

### Kenapa ini masalah?

**Django-allauth TIDAK MEMBACA dict bernama `ACCOUNT_SETTINGS`.** Allauth nyari setting bernama langsung seperti `ACCOUNT_LOGIN_METHODS`, `ACCOUNT_EMAIL_REQUIRED`, dst. di namespace settings. Karena kamu bungkus dalam dict, allauth nggak pernah tau settingnya — fallback ke default semua.

Log server lama juga udah ngasih warning:
```
settings.ACCOUNT_AUTHENTICATION_METHOD is deprecated,
use: settings.ACCOUNT_LOGIN_METHODS = {'email'}
```

### Cara fix

Unwrap dict-nya:

```python
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'  # atau 'mandatory' kalau mau email verify
```

### Pelajaran fullstack

**Konsep: Library settings convention.** Setiap library di Django biasanya pakai prefix di setting name (`ACCOUNT_`, `SOCIALACCOUNT_`, `REST_`, `CELERY_`, dst). Mereka baca pakai `getattr(django_settings, 'ACCOUNT_LOGIN_METHODS', default)`. Kalau kamu bungkus dalam dict, `getattr` akan miss dan pakai default.

Selalu cek dokumentasi resmi library untuk nama setting yang tepat — jangan asumsi.

---

## Bug #4 — `AUTHENTICATION_BACKENDS` Nggak Lengkap

### Apa masalahnya?

Di settings.py yang aktif (baris 86–88):

```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
```

Tapi `allauth.account.middleware.AccountMiddleware` udah ditambahin di MIDDLEWARE.

### Kenapa ini masalah?

Allauth perlu backend-nya sendiri untuk autentikasi (terutama buat social login / email login). Tanpa backend allauth, login via Google (`GOOGLE_CLIENT_ID` di README) nggak bakal jalan, dan email-based login allauth juga bypass.

### Cara fix

```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
```

### Pelajaran fullstack

**Konsep: Authentication middleware chain.** Django bisa punya multiple backends, dicek satu-satu sampai salah satu return user. `ModelBackend` = Django default (username+password cek ke DB). `AllauthBackend` = support login via email verification link, social login, dsb.

---

## Bug #5 — Dua `settings.py` Berbeda

### Apa masalahnya?

Ada:
- `Anotasi_Image/settings.py` (flat, yang aktif karena `DJANGO_SETTINGS_MODULE = 'settings'`)
- `Anotasi_Image/Anotasi_Image/settings.py` (nested, tidak aktif)

Isinya berbeda signifikan: yang nested punya `ROOT_URLCONF = 'Anotasi_Image.urls'`, yang flat punya `ROOT_URLCONF = 'urls'`.

### Kenapa ini masalah?

Kebingungan maintenance. Orang baru di tim buka yang nested, nge-edit, frustrasi karena nggak ada efek. Atau kebalikannya — dua settings di-edit berbeda dan nanti bug muncul pas deploy.

Juga bahaya karena folder `Anotasi_Image/Anotasi_Image/` masih ada di sys.path kalau konfigurasi diubah, bisa import yang salah.

### Cara fix

Pilih struktur standard Django:
```
Anotasi_Image/                 <-- project root (sama level dengan manage.py)
├── manage.py
├── Anotasi_Image/             <-- package dengan nama sama
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── master/
├── annotator/
└── reviewer/
```

Delete `Anotasi_Image/settings.py` dan `Anotasi_Image/urls.py` yang flat. Update `manage.py`:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Anotasi_Image.settings')
```

Update settings nested:
```python
ROOT_URLCONF = 'Anotasi_Image.urls'
WSGI_APPLICATION = 'Anotasi_Image.wsgi.application'
```

### Pelajaran fullstack

**Konsep: Convention over configuration.** Django punya struktur standar — ikutin aja. Kalau bikin struktur custom, harus konsisten di semua tempat (`manage.py`, `wsgi.py`, `asgi.py`, deployment config).

---

## Bug #6 — `DJANGO_SETTINGS_MODULE = 'settings'` (fragile)

### Apa masalahnya?

Di `manage.py`:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
```

### Kenapa ini masalah?

Ini cuma jalan karena kebetulan `manage.py` dan `settings.py` ada di folder yang sama (jadi Python bisa import `settings` sebagai top-level module). Begitu kamu pindahin atau deploy pake gunicorn dari direktori lain, langsung error.

### Cara fix

Seperti di bug #5: gunakan path package:
```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Anotasi_Image.settings')
```

### Pelajaran fullstack

**Konsep: Python import path (sys.path).** Python import itu relatif ke `sys.path`. Nama module tanpa prefix = top-level module. Kalau project scale, selalu pake dotted path (`package.module`) — lebih eksplisit & portable.

---

## Bug #7 — Class `User` Legacy di `master/models.py`

### Apa masalahnya?

Baris 8–24 ada class `User` sendiri (bukan AbstractUser), padahal `AUTH_USER_MODEL = 'master.CustomUser'` (baris 84 settings).

### Kenapa ini masalah?

- Class `User` itu terbuat tabel tersendiri di DB (waste of space)
- Developer baru bingung: mana yang dipakai? Apakah mereka related?
- Potensi bug: kalau orang lain impor `from master.models import User`, mereka pikir itu Django User padahal bukan.

### Cara fix

Hapus class `User` (baris 8–24). Kalau perlu track role, udah ada di `CustomUser.role`.

### Pelajaran fullstack

**Konsep: Dead code.** Kode yang nggak dipake tapi nggak dihapus = hutang teknis. Gunakan tools seperti `vulture` atau `flake8` untuk deteksi.

---

## Bug #8 — `ALLOWED_HOSTS` Terlalu Longgar

### Apa masalahnya?

```python
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "172.16.1.54",
    "ba81abbf02db.ngrok-free.app",
    "*",     # <-- ini ngebypass semua
]
```

### Kenapa ini masalah?

`"*"` = terima request dari host apapun. Ini fitur keamanan Django untuk mencegah Host header injection attack. Dengan `"*"`, proteksi ini mati.

Untuk DEV lokal ok, tapi kalau kamu deploy ke internet dengan setting ini, kamu terbuka terhadap serangan.

### Cara fix

Pindah ke env var:

```python
# settings.py
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

Terus di `.env`:
```
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

### Pelajaran fullstack

**Konsep: Twelve-Factor App — "Config in Environment".** Setting yang beda antar dev/staging/prod harus di env var, bukan hardcoded. Baca: https://12factor.net/config

---

## Bug #9 — AI API URL Hardcoded

### Apa masalahnya?

Di `annotator/views.py` baris 17:

```python
AI_API_URL = "https://pursue-various-engineer-corporate.trycloudflare.com/api/proses-gambar/"
```

### Kenapa ini masalah?

- URL cloudflare-tunnel itu temporary (berubah tiap restart tunnel)
- Kalau URL-nya berubah, harus edit kode & deploy ulang
- Di test env nggak bisa ganti ke mock server

### Cara fix

Pindah ke env var:
```python
# annotator/views.py
AI_API_URL = os.getenv('AI_API_URL', 'http://localhost:8080/api/proses-gambar/')
```

Di `.env`:
```
AI_API_URL=https://pursue-various-engineer-corporate.trycloudflare.com/api/proses-gambar/
```

### Pelajaran fullstack

**Konsep: External service configuration.** Setiap service eksternal (API, database, cache) harus configurable via env. Bagus juga untuk naro timeout & retry config.

---

## Bug #10 — File Sampah di Root

### Apa masalahnya?

Di root project ada file-file:
- `check_annotations_job22.py`
- `check_annotations.py`
- `debug_annotations.py`
- `fix_existing_annotations.py`
- `datadummy.sql`
- `test_api_endpoint.py`
- `test_api_simple.py`
- `cookies.txt`
- `server_output.log`
- `WORK_SESSION_HISTORY.md` (0 byte)
- `FETCH_HEAD`, `FETCH_HEAD 2` (0 byte)
- 15+ file markdown dokumentasi

### Kenapa ini masalah?

Bikin project kelihatan messy, developer baru bingung mana yang kepake vs debug sementara. Juga `cookies.txt` ikut ke-commit — potensi bocor session.

### Cara fix

```
project/
├── scripts/         # taro semua file utility (migrate, check, debug)
├── docs/            # taro semua MD dokumentasi
├── tests/           # test files yang proper
└── .gitignore       # tambahin cookies.txt, *.log, FETCH_HEAD
```

### Pelajaran fullstack

**Konsep: Project hygiene.** Jaga root folder rapi — cuma hal esensial (manage.py, README.md, requirements.txt, config). Bikin .gitignore yang cukup.

---

## Belajar Fullstack: Alur Request di Project Ini

Biar paham kenapa tiap bug di atas muncul, ini alur request Django secara umum:

```
Browser request
    │
    ▼
Anotasi_Image/urls.py       (ROOT_URLCONF — entry point URL)
    │
    ├── '' → master.urls → views.py → template
    ├── 'annotator/' → annotator.urls → views.py → template
    └── 'reviewer/' → reviewer.urls → views.py → template
                                      │
                                      ▼
                              master.models.py  (database layer)
                                      │
                                      ▼
                              db.sqlite3
```

### Komponen-komponen

| Layer | File | Fungsi |
|-------|------|--------|
| Routing | `urls.py` | Map URL ke view function |
| View | `views.py` | Logic: ambil data, render response |
| Model | `models.py` | Schema DB + query methods |
| Template | `templates/*.html` | HTML rendering |
| Static | `static/*.css, *.js` | Asset frontend |
| Middleware | `settings.MIDDLEWARE` | Process request & response (auth, csrf) |

### Di project ini, alur "label gambar" misalnya:

1. User buka `/annotator/label/5/3/` (job_id=5, image_id=3)
2. `Anotasi_Image/urls.py` → match `annotator/` → delegate ke `annotator/urls.py`
3. `annotator/urls.py` → match `label/<int:job_id>/<int:image_id>/` → panggil `views.label_image_view`
4. `views.label_image_view`:
   - Cek `@annotator_required` (decorator auth) — kalau bukan annotator, redirect
   - Query `JobImage.objects.get(id=image_id)` (master.models.JobImage)
   - Render template `annotator/label.html`
5. Browser dapat HTML, user anotasi, kirim POST ke `send-image/<image_id>/`
6. `send_image_view` → panggil AI API → dapat bbox → simpan ke `Annotation`
7. **BUG ada di step 7 ini** — simpan pake `image=`, nanti read pake `job_image=`. Mismatch!

---

## Rekomendasi Urutan Perbaikan

Jangan fix semua sekaligus. Urutan yang saya saranin:

1. **Setup dulu di lokal:** Fix bug #5, #6 (struktur settings) → bisa runserver.
2. **Allauth:** Fix bug #3, #4 → login/logout jalan normal.
3. **Data integrity:** Fix bug #1, #2 → annotasi bisa disimpan & dibaca bener.
4. **Cleanup:** Bug #7, #10 → project rapi.
5. **Security:** Bug #8, #9 → siap deploy.

Tiap step, **jalankan migration** (`makemigrations` + `migrate`) dan **test manual** sebelum lanjut ke step berikutnya. Jangan loncat.

---

## Materi Belajar Fullstack dari Project Ini

Project kamu actually punya banyak konsep bagus yang bisa kamu dalami. Saya urutkan dari fundamental ke advanced:

### Fundamental (minggu 1–2)
- **MVC / MVT pattern** — Django pakai MVT (Model-View-Template). Pelajari tanggung jawab tiap layer.
- **ORM & Migration** — `models.py` → `makemigrations` → `migrate`. Pelajari kenapa kita nggak nulis SQL langsung.
- **URL routing** — `path()`, `include()`, URL namespace (`app_name`).

### Menengah (minggu 3–4)
- **Auth & Permissions** — `@login_required`, custom decorator (kayak `@annotator_required`), AUTH_USER_MODEL.
- **Form handling** — POST/GET, CSRF token, validation (Django Forms).
- **File upload** — `FileField`, `ImageField`, MEDIA_ROOT, MEDIA_URL.

### Advanced (bulan 2+)
- **Class-based views** — ListView, DetailView, FormView.
- **Django REST Framework** — biar frontend React/Vue bisa fetch JSON API.
- **Async task** — Celery + Redis (untuk AI processing di background, biar UI nggak stuck).
- **Testing** — `pytest-django`, factory_boy, integration test.
- **Deployment** — Gunicorn + Nginx, Docker, PostgreSQL (dari SQLite).

### Frontend (paralel)
- Pelajari JavaScript modern (ES6+, async/await, fetch)
- Di project ini HTML/CSS/JS masih tradisional — next level: pakai React/Vue untuk annotator UI, plus Konva.js atau Fabric.js buat canvas gambar.

---

## Penutup

Project kamu udah lumayan komprehensif — ada multi-role (master/annotator/reviewer), upload, AI integration, notification. Bug yang ada mostly karena iterasi cepat & refactor setengah jalan. Nggak apa-apa — semua project kayak gini kalau developer solo.

Next step: kerjain urutan perbaikan di atas satu-satu, dan update README sama sekalian. Kalau ada bug yang pas ngerjain bikin stuck, balik lagi ke chat ini — saya bantu debug lebih dalam.

— Semangat belajar fullstack!
