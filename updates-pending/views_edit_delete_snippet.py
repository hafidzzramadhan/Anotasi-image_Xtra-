"""
SNIPPET — Edit & Delete Job Profile
===================================
Copy 2 fungsi di bawah ini, paste ke AKHIR file master/views.py
(sebelum atau sesudah view yang udah ada, bebas)

Decorator @login_required dan @require_http_methods udah di-import di
views.py lu (dipakai oleh create_job_profile), jadi gak perlu import
tambahan.
"""


# ========================================================
# EDIT JOB PROFILE
# ========================================================
@login_required
@require_http_methods(["GET", "POST"])
def edit_job_profile(request, job_id):
    """
    GET  -> return current job data (buat prefill form edit)
    POST -> update job & return success
    """
    try:
        job = JobProfile.objects.get(id=job_id)
    except JobProfile.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Job profile tidak ditemukan'},
            status=404
        )

    if request.method == 'GET':
        return JsonResponse({
            'status': 'success',
            'data': {
                'id': job.id,
                'title': job.title,
                'description': job.description or '',
                'segmentation_type': job.segmentation_type or '',
                'shape_type': job.shape_type or '',
                'color': job.color or '#000000',
                'priority': job.priority or 'medium',
                'start_date': job.start_date.strftime('%Y-%m-%d') if job.start_date else '',
                'end_date': job.end_date.strftime('%Y-%m-%d') if job.end_date else '',
            }
        })

    # POST — update
    try:
        job.title = request.POST.get('title', job.title)
        job.description = request.POST.get('description', job.description)
        job.segmentation_type = request.POST.get('segmentation', job.segmentation_type)
        job.shape_type = request.POST.get('shape', job.shape_type)
        job.color = request.POST.get('color', job.color)
        job.priority = request.POST.get('priority', job.priority)

        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        if start_date:
            job.start_date = start_date
        if end_date:
            job.end_date = end_date

        job.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Job profile berhasil di-update',
            'id': job.id,
        })
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=500
        )


# ========================================================
# DELETE JOB PROFILE
# ========================================================
@login_required
@require_http_methods(["POST"])
def delete_job_profile(request, job_id):
    """
    Hard-delete job profile. Juga hapus semua JobImage, Annotation, dll
    yang berelasi (on_delete=CASCADE di model).
    """
    try:
        job = JobProfile.objects.get(id=job_id)
        job_title = job.title
        job.delete()
        return JsonResponse({
            'status': 'success',
            'message': f'Job profile "{job_title}" berhasil dihapus'
        })
    except JobProfile.DoesNotExist:
        return JsonResponse(
            {'status': 'error', 'message': 'Job profile tidak ditemukan'},
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=500
        )
