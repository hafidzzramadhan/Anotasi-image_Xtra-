# ============================================================
# PATCH untuk views.py — function performance_individual_view
# ============================================================
#
# LOKASI: master/views.py (sekitar line 1253)
# TUJUAN: Tambahin user_jobs_list di context biar template baru
#         bisa nampilin list job yang di-handle user itu (fitur baru).
#
# PERUBAHAN: 2 step kecil
# ============================================================

# ============================================================
# STEP 1 — Cari baris ini di performance_individual_view (sekitar line 1371):
# ============================================================
#
#     context = {
#         'user_profile': {
#             'name': f"{user.first_name} {user.last_name}".strip() or user.username,
#             ...
#         },
#         'user_stats': {
#             ...
#         }
#     }
#
# ============================================================
# STEP 2 — SEBELUM baris `context = {`, tempel blok kode ini:
# ============================================================

    # === BUILD JOB LIST dengan progress percentage per job ===
    user_jobs_list = []
    for job in user_jobs.order_by('-date_created'):
        # Hitung progress per job (finished / total images)
        job_images_qs = JobImage.objects.filter(job=job)
        total_img = job_images_qs.count()
        finished_img = job_images_qs.filter(status='finished').count()
        progress = round((finished_img / total_img * 100)) if total_img > 0 else 0

        # Ambil URL first image (buat thumbnail di template)
        first_image = job_images_qs.first()
        first_image_url = None
        if first_image and first_image.image:
            try:
                first_image_url = first_image.image.url
            except Exception:
                first_image_url = None

        user_jobs_list.append({
            'id': job.id,
            'title': job.title,
            'description': job.description or '',
            'status': job.status,
            'image_count': total_img,
            'progress_percentage': progress,
            'first_image_url': first_image_url,
        })


# ============================================================
# STEP 3 — TAMBAHIN 'user_jobs_list': user_jobs_list di dalam context dict.
# Jadi isinya jadi kaya gini:
# ============================================================

    context = {
        'user_profile': {
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'email': user.email,
            'role': user.role,
            'status': user_status,
            'status_class': status_class,
        },
        'user_stats': {
            'total_jobs': total_jobs,
            'total_images': total_images,
            'chart_data': job_chart_data,
            'image_chart_data': image_chart_data,
        },
        # --- BARU ---
        'user_jobs_list': user_jobs_list,
    }

    return render(request, "master/performance_individual.html", context)


# ============================================================
# PENJELASAN:
# ============================================================
#
# - user_jobs sudah ada di function ini (line 1262 atau 1264).
# - Kita loop semua job user, hitung progress nya, ambil thumbnail.
# - Di-pass sebagai user_jobs_list ke template.
# - Template pake data ini buat nampilin cards list of jobs.
#
# ============================================================
# KALAU MASALAH: Template bilang "user_jobs_list" undefined, itu
# artinya STEP 3 belum dilakuin — pastiin 'user_jobs_list':
# user_jobs_list MASUK ke dalam context dict.
# ============================================================
