# ============================================================
# PATCH untuk views.py — function home_view
# ============================================================
#
# LOKASI: master/views.py (sekitar line 180-273)
# TUJUAN: Template home.html yang baru butuh 3 variable tambahan
#         di context: unannotated_count, in_progress_count, issues_count
#
# CARA: Cari baris `context = {` di home_view (sekitar line 267),
#       GANTI dict nya dengan dict baru di bawah ini.
# ============================================================

# ============================================================
# STEP 1 — Tambahin ini SEBELUM baris `context = {`
# (taruh setelah assignment_stats selesai dihitung)
# ============================================================

    # Count images with 'Issue' status (case-sensitive, match dengan issue_solving_view)
    issues_count = JobImage.objects.filter(status='Issue').count()

    # In progress = in_review + in_rework (gabungan stage tengah)
    in_progress_count = in_review_count + in_rework_count


# ============================================================
# STEP 2 — GANTI `context = {...}` dengan ini:
# ============================================================

    context = {
        'users': CustomUser.objects.all(),
        'datasets': Dataset.objects.all().order_by('-date_created'),
        'status_list': status_list,
        'assignment_stats': assignment_stats,
        # --- 3 VARIABLE BARU ---
        'unannotated_count': unannotated_count,
        'in_progress_count': in_progress_count,
        'issues_count': issues_count,
    }
    return render(request, 'master/home.html', context)


# ============================================================
# PENJELASAN TIAP VARIABLE BARU:
# ============================================================
#
# unannotated_count
#   - Udah ada di line 230 (unannotated_count = JobImage.objects.filter(status='unannotated').count())
#   - TINGGAL di-add ke context dict
#
# in_progress_count
#   - Gabungan in_review + in_rework
#   - Ditampilin di KPI card "Sedang Berjalan"
#
# issues_count
#   - Count image yang statusnya 'Issue' (huruf gede, match issue_solving_view)
#   - Ditampilin di KPI card "Issue Butuh Review" (merah dengan indikator blinking)
#
# ============================================================
# KALO SETELAH PATCH ADA ERROR KaraNA VARIABLE BELUM DI-DEFINE:
# ============================================================
# Kalo template error bilang "variable not defined", itu karna home_view lama
# mungkin beda sedikit. Paling aman: PASTIIN 3 variable ini dihitung SEBELUM
# context = {...} dan DI-ADD ke dalam dict context.
#
# Kalo ragu, paste aja keseluruhan home_view di bawah ini buat REPLACE total:
# ============================================================

"""
@master_required
def home_view(request):
    # Real data for Status Section
    annotators_reviewers = CustomUser.objects.filter(role__in=['annotator', 'reviewer']).order_by('email')

    status_list = []
    for user in annotators_reviewers:
        has_active_jobs = False
        if user.role == 'annotator':
            has_active_jobs = JobProfile.objects.filter(worker_annotator=user, status__in=['in_progress']).exists()
        elif user.role == 'reviewer':
            has_active_jobs = JobProfile.objects.filter(worker_reviewer=user, status__in=['in_progress']).exists()

        if has_active_jobs:
            status = 'In Job'
            status_class = 'text-blue-700 bg-blue-100'
        else:
            has_any_jobs = False
            if user.role == 'annotator':
                has_any_jobs = JobProfile.objects.filter(worker_annotator=user).exists()
            elif user.role == 'reviewer':
                has_any_jobs = JobProfile.objects.filter(worker_reviewer=user).exists()

            if has_any_jobs:
                status = 'Ready'
                status_class = 'text-green-700 bg-green-100'
            else:
                status = 'Not Ready'
                status_class = 'text-red-700 bg-red-100'

        status_list.append({
            'name': f"{user.first_name} {user.last_name}".strip() or user.email,
            'status': status,
            'status_class': status_class
        })

    # Assignment stats
    total_images = JobImage.objects.count()
    unannotated_count = JobImage.objects.filter(status='unannotated').count()
    in_review_count = JobImage.objects.filter(status='in_review').count()
    in_rework_count = JobImage.objects.filter(status='in_rework').count()
    finished_count = JobImage.objects.filter(status='finished').count()
    issues_count = JobImage.objects.filter(status='Issue').count()
    in_progress_count = in_review_count + in_rework_count
    assigned_count = total_images - unannotated_count

    assignment_stats = {
        'total': total_images,
        'assign': assigned_count,
        'progress': in_review_count,
        'reviewing': in_rework_count,
        'finished': finished_count,
    }

    context = {
        'users': CustomUser.objects.all(),
        'datasets': Dataset.objects.all().order_by('-date_created'),
        'status_list': status_list,
        'assignment_stats': assignment_stats,
        'unannotated_count': unannotated_count,
        'in_progress_count': in_progress_count,
        'issues_count': issues_count,
    }
    return render(request, 'master/home.html', context)
"""
