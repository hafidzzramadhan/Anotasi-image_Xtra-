# 🚀 Integration Guide — Anotasi Image

Panduan integrasi untuk lu sama temen (Annotator & Reviewer) setelah initial push.

---

## 📋 Status Saat Ini

| Komponen | Status |
|---|---|
| 🎨 Template redesign (`master/templates/master/`) | ✅ **DONE** — udah applied |
| 🧩 Base template (`templates/base_master.html`) | ✅ **DONE** — sidebar metallic purple |
| 🐍 Views.py patches | ⏳ **PENDING** — ada di `updates-pending/` |
| 🗄️ PostgreSQL migration | ⏳ **PENDING** — script di `updates-pending/` |
| 👥 Backend Annotator & Reviewer | 🔵 Original dari temen (blm diubah) |

---

## 📁 Struktur Folder

```
Anotasi-image_Xtra-/
├── Anotasi_Image/              ← Django project root
│   ├── master/                 ← Backend role MASTER (punya lu)
│   │   ├── models.py           ⚠️ shared — bahas dulu kalau mau diubah
│   │   ├── views.py            ⏳ perlu di-patch manual (lihat updates-pending/)
│   │   ├── urls.py
│   │   └── templates/master/   ✅ udah di-redesign
│   ├── annotator/              ← Backend role ANNOTATOR (temen 1)
│   ├── reviewer/               ← Backend role REVIEWER (temen 2)
│   ├── templates/              ← Base templates (shared)
│   │   └── base_master.html    ✅ udah pake sidebar baru
│   ├── Anotasi_Image/          ← settings.py, urls.py (root config)
│   └── manage.py
├── updates-pending/            ⏳ Patch yang belum di-apply
├── media/                      ← User uploads (di-gitignore utk produksi)
├── requirements.txt
└── README.md
```

---

## 👥 Setup Collaborator (LU LAKUIN DULU)

1. **Invite temen sebagai collaborator** di GitHub:
   - Buka: https://github.com/hafidzzramadhan/Anotasi-image_Xtra-/settings/access
   - Click **"Add people"** → masukin username/email temen
   - Kasih permission **"Write"** (biar bisa push ke branch)

2. **Branch strategy yang gw rekomendasiin:**
   ```
   main              ← stable code (protected, cuma merge via PR)
   ├── dev-master    ← lu kerja di sini
   ├── dev-annotator ← temen 1 kerja di sini
   └── dev-reviewer  ← temen 2 kerja di sini
   ```

3. **Protect branch `main`** (optional tapi recommended):
   - Settings → Branches → Add rule → pattern: `main`
   - ✅ Require pull request before merging
   - ✅ Require review from 1 person

---

## 🔧 Cara Temen Lu Clone & Kerja

```bash
# Temen 1 (Annotator) — di laptop dia:
git clone https://github.com/hafidzzramadhan/Anotasi-image_Xtra-.git
cd Anotasi-image_Xtra-

# Setup virtual env
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Bikin branch sendiri
git checkout -b dev-annotator

# Kerja di folder Anotasi_Image/annotator/
# ... edit ...

# Run server buat test
cd Anotasi_Image
python manage.py migrate
python manage.py runserver

# Kalau udah selesai editing:
git add Anotasi_Image/annotator/
git commit -m "Fix bug X di annotator"
git push origin dev-annotator

# Buka Pull Request di GitHub → lu review → merge ke main
```

Temen Reviewer sama, tinggal ganti `dev-annotator` jadi `dev-reviewer` dan fokus di folder `Anotasi_Image/reviewer/`.

---

## ⏳ Yang Harus Lu Apply Manual (updates-pending/)

Karena patch ini ngubah logic backend, gw sengaja gak auto-apply biar lu bisa review dulu:

### 1. `views_home_patch.py`
Tambahan context di `home_view` buat nampilin stats/grafik yang dipake home.html baru.

**Cara apply:**
1. Buka `Anotasi_Image/master/views.py`
2. Cari function `def home_view(request):`
3. Tempel block dari file patch ke lokasi yang di-indicate
4. Save

### 2. `views_performance_patch.py`
Tambahan `user_jobs_list` di context `performance_individual_view` biar template bisa nampilin list job per user.

### 3. `views_issue_detail_patch.py`
Perbaikan JSON response di `issue_detail_view`.

### 4. `views_edit_delete_snippet.py`
Function baru: `edit_dataset_view`, `delete_dataset_view`.

### 5. `urls_snippet.py`
URL pattern baru yang match dengan function di #4 (dataset edit/delete).

### 6. PostgreSQL migration
- `MIGRATE_TO_POSTGRESQL.md` — step-by-step guide
- `migrate_sqlite_to_postgres.sh` — script otomatis
- `settings_DATABASES_snippet.py` — config DATABASES baru
- `.env.example` — template env vars

**⚠️ CATATAN:** Migration SQLite → PostgreSQL opsional. Kalau sekarang masih dev dan data kecil, SQLite cukup. PostgreSQL wajib kalau udah siap deploy production.

---

## 📞 Shared Files — Butuh Komunikasi

File-file ini dipake lebih dari 1 role. **Jangan main edit sendiri — bahas dulu di grup:**

| File | Dipake oleh | Kenapa sensitif |
|---|---|---|
| `Anotasi_Image/master/models.py` | Master, Annotator, Reviewer | Shared database schema |
| `Anotasi_Image/Anotasi_Image/settings.py` | All | Config global |
| `Anotasi_Image/Anotasi_Image/urls.py` | All | Root URL routing |
| `requirements.txt` | All | Dependencies |

Kalau butuh ngubah salah satu di atas: bikin issue dulu di GitHub, diskusiin, baru apply.

---

## 🆘 Troubleshooting

**"Static file gak muncul (logo, dll)"**
→ Save logo upload lu ke `Anotasi_Image/static/images/logo-anotasi.png`, lalu `python manage.py collectstatic`.

**"Template Error: base_master.html not found"**
→ Pastiin di `settings.py` ada:
```python
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],  ← ini penting
    ...
}]
```

**"db.sqlite3 gak ada setelah clone"**
→ Run `python manage.py migrate` buat bikin DB baru. Data awal bisa di-load dari `datadummy.sql`.

**"Permission denied pas push"**
→ Pastiin udah di-invite sebagai collaborator (step setup di atas).

---

## 📦 File yang TIDAK di-commit

Cek `.gitignore` — yang di-skip:
- `.venv/` — virtualenv
- `__pycache__/`, `*.pyc` — Python cache
- `db.sqlite3` — database local (tiap orang bikin sendiri)
- `media/` — user uploads (tergantung policy, bisa di-commit kalau perlu sample data)
- `.env` — secret credentials

Kalau ada file di atas yang sebenernya perlu di-commit (misal `media/sample_images/`), hapus baris yang relevan di `.gitignore`.

---

*Generated by AI assistant. Update as the project grows.*
