# Roadmap 5 Bulan — Anotasi Image (Magang Projek Dosen)

> **Konteks:** Solo full-time dulu → kolaborasi tim setara → deploy final 5 bulan
> **Prinsip:** Pelan-pelan tapi konsisten. Fondasi dulu, fitur kemudian.

---

## Big Picture: 5 Bulan dalam Satu Gambar

```
Bulan 1 ████████████████ FONDASI & MASTER ROLE  (solo)
Bulan 2 ████████████████ ANNOTATOR ROLE          (solo)
Bulan 3 ████████████████ REVIEWER ROLE           (solo/ajak temen review)
Bulan 4 ████████████████ KOLABORASI + INTEGRATION (tim masuk!)
Bulan 5 ████████████████ POLISH + STAGING + DEPLOY FINAL
```

Alasan split begini:
- **Bulan 1-3 solo** → kamu paham 100% codebase dulu. Saat temen masuk, kamu jadi "senior" yang bisa jawab semua pertanyaan.
- **Bulan 4 invite temen** → arsitektur udah matang, fitur core udah ada. Temen tinggal tambah polish & feature baru.
- **Bulan 5 buffer** → production ada banyak drama yang nggak ketebak. Jangan planning tight.

---

## Bulan 1 — Fondasi + Role Master

### Week 1: Project Hygiene (sekarang!)
- [ ] Restructure settings jadi module (`base.py`, `development.py`, `production.py`)
- [ ] Hapus file duplikat & debug scripts
- [ ] Setup `.env.example`, `.gitignore`
- [ ] Fix bug struktural #1-#5 dari laporan debug
- [ ] Setup Docker Compose (Postgres + Django)
- [ ] Update README (Quick Start 5 menit)

### Week 2: PostgreSQL Migration
- [ ] Install Postgres lokal via Docker
- [ ] Migrate SQLite → Postgres (fresh install)
- [ ] Fix `CustomUser` auth flow + allauth setup
- [ ] Test role-based redirect (master/annotator/reviewer)

### Week 3-4: Master Role Stabilize
- [ ] Model review & index (JobProfile, JobImage, Dataset, Notification)
- [ ] Dashboard master (stats: job active, annotator performance)
- [ ] Upload dataset (handle ZIP, validate format)
- [ ] Create job + assign worker (annotator & reviewer)
- [ ] Basic unit test untuk logic penting

**Deliverable Bulan 1:**
- Project clean, dockerized, di Postgres
- Master bisa login, bikin job, assign worker
- Demo-able ke dosen

---

## Bulan 2 — Role Annotator (Core Feature)

### Week 1-2: Annotator Flow Dasar
- [ ] Fix bug `image` vs `job_image` (bug #2)
- [ ] Login annotator, dashboard list job ditugasin
- [ ] Detail job: list gambar dengan status
- [ ] Notification: "Job baru ditugasin ke kamu"

### Week 3: Canvas Annotation UI
- [ ] Integrasi library canvas (pilih: Konva.js / Fabric.js / Leaflet)
- [ ] Bounding box tool
- [ ] Polygon tool (buat segmentation)
- [ ] Label picker dropdown (dari segmentation_type job)

### Week 4: AI Auto-Annotate Integration
- [ ] Pindah `AI_API_URL` ke env var
- [ ] Handle timeout & retry
- [ ] Save detection result ke model Annotation
- [ ] User bisa edit/delete AI hasil

**Deliverable Bulan 2:**
- Annotator bisa anotasi gambar end-to-end
- AI auto-annotate jalan
- Finish annotation → status berubah ke "in_review"

---

## Bulan 3 — Role Reviewer + Issue System

### Week 1-2: Reviewer Flow
- [ ] Login reviewer, list image ready to review
- [ ] View annotasi annotator (read-only)
- [ ] Approve / Reject / Request Rework

### Week 3: Issue System
- [ ] Bikin issue di image/annotasi tertentu
- [ ] Comment thread di issue
- [ ] Attach screenshot/file
- [ ] Assign balik ke annotator untuk fix

### Week 4: Workflow Testing + Bug Fix
- [ ] End-to-end test: master → annotator → reviewer → annotator rework → reviewer approve → finish
- [ ] Fix bug yang muncul dari integration test
- [ ] Code cleanup + lint

**Deliverable Bulan 3:**
- Tiga role fully functional
- Workflow lengkap jalan
- Ready untuk invite temen

---

## Bulan 4 — Kolaborasi + Integration (TEMEN MASUK!)

### Week 1: Onboarding Temen
- [ ] Dokumentasi arsitektur (buat temen paham codebase)
- [ ] Setup GitHub Projects / Jira / Trello untuk task tracking
- [ ] Branching rule & PR template
- [ ] Pair programming 2-3 hari (kamu jelasin, temen ngikut)

### Week 2-3: Fitur Lanjutan (paralel)
Split berdasarkan ownership:
- **Kamu** (DevOps + Master): Performance tracking, reporting, deploy pipeline
- **Teman A** (Annotator): UI polish, keyboard shortcut, multi-label
- **Teman B** (Reviewer): Bulk review, export annotasi (COCO/YOLO format)

### Week 4: Integration Tests
- [ ] E2E test dengan Cypress/Playwright (atau manual checklist)
- [ ] Load test (seberapa banyak user concurrent masih OK?)
- [ ] Security audit (dari checklist production)

**Deliverable Bulan 4:**
- Fitur lengkap untuk skala tim
- Tim udah nyaman sama codebase
- Staging environment berjalan

---

## Bulan 5 — Hardening + Staging + Deploy Final

### Week 1: Staging Deploy
- [ ] Pilih platform (Railway/Render dulu, pindah AWS kalau perlu)
- [ ] Setup Postgres managed (Supabase/Neon free tier)
- [ ] Setup object storage untuk media (Cloudflare R2 / S3)
- [ ] CI/CD (GitHub Actions: test → build → deploy)

### Week 2: User Acceptance Testing
- [ ] Undang dosen + user asli (annotator real)
- [ ] Track feedback di GitHub Issues
- [ ] Fix critical bugs only (defer nice-to-have)

### Week 3: Production Hardening
- [ ] Monitoring (Sentry + uptime checker)
- [ ] Backup otomatis + test restore
- [ ] SSL + HSTS + security headers
- [ ] Rate limiting

### Week 4: Final Deploy + Dokumentasi
- [ ] Deploy ke production domain
- [ ] User manual (untuk annotator & reviewer)
- [ ] Tech documentation (untuk handover nanti)
- [ ] Demo ke dosen

**Deliverable Bulan 5:**
- Aplikasi live, dipake user real
- Dokumentasi lengkap
- Magang SELESAI dengan bangga!

---

## Ritme Harian yang Saya Saranin

Karena full-time + sendiri dulu, gampang burnout. Ritme ini sustainable:

```
09:00 - 10:00   Standup sendiri: review yesterday, plan today
10:00 - 12:00   Deep work (fitur utama hari ini)
12:00 - 13:00   Lunch + jalan-jalan (WAJIB keluar ruangan)
13:00 - 15:00   Deep work lanjutan
15:00 - 15:30   Break (bukan scroll HP, tapi istirahat mata)
15:30 - 17:00   Code review diri sendiri + refactor
17:00 - 17:30   Commit + push + tulis progress log
```

**Aturan:**
- Max 2 deep work session per hari. Kalau lebih, quality turun.
- Setiap Jumat: no coding, cuma refactor + dokumentasi.
- Setiap akhir bulan: review terhadap roadmap, adjust kalau perlu.

---

## Checkpoint ke Dosen

Bikin meeting rutin sama dosen biar sinkron:

- **Akhir Bulan 1:** Demo setup & master role
- **Akhir Bulan 2:** Demo annotator + AI integration
- **Akhir Bulan 3:** Demo workflow lengkap (3 role)
- **Akhir Bulan 4:** Demo kolaborasi tim + staging
- **Akhir Bulan 5:** Final demo production

---

## Risiko yang Harus Diwaspadai

1. **Scope creep** — dosen mendadak minta fitur baru. Sikapi: catat di backlog, tapi jangan masuk scope sekarang.
2. **Temen beda pace** — kalau temen lebih lambat/cepat, arsitektur harus fleksibel. Makanya split by app (master/annotator/reviewer) biar independent.
3. **AI API mati** — kamu pake Cloudflare tunnel URL, pasti temporary. Fase 2 Week 4 harus handle ini.
4. **Deploy drama** — budget 2 minggu untuk "hal-hal yang nggak ketebak" di Bulan 5.
5. **Burnout** — bulan 3 biasanya titik lelah. Break seminggu kalau perlu.

---

## Alat yang Saya Saranin Pakai

| Kategori | Tool | Kenapa |
|---|---|---|
| IDE | VS Code / PyCharm | Debug Django enak |
| API testing | Bruno / Postman | Test endpoint tanpa frontend |
| DB GUI | DBeaver / pgAdmin | Query postgres tanpa terminal |
| Git GUI | GitHub Desktop / GitKraken | Visual commit history |
| Diagram | Excalidraw / drawio | Bikin arsitektur diagram |
| Task tracking | GitHub Projects | Free, terintegrasi dengan repo |
| Chat tim | Discord / Slack | Voice call easy |
| Dokumentasi | Markdown in repo | Self-contained, versi control |
| Deploy awal | Railway / Render | Free tier, simple |
| Deploy final | Tergantung budget dosen | Pilih saat Bulan 5 |

---

## Mulai Hari Ini: Fase 1 Week 1

Saya akan pandu Step 1 sekarang: **Restructure settings**.

Alasan mulai dari sini:
1. Paling mendasar — semua step lain butuh settings yang benar.
2. Paling gampang — nggak butuh coding fitur, cuma rename & pindah file.
3. Langsung fix bug #5 dari laporan debug (dua settings.py).
4. Bikin kamu familiar sama konsep "settings module pattern" yang dipakai di semua project Django enterprise.

Stay tuned, saya kasih step demi step.
