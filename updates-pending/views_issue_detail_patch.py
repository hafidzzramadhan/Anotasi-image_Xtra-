# ============================================================
# PATCH untuk views.py — function issue_detail_view
# ============================================================
#
# LOKASI: master/views.py
# FUNGSI: issue_detail_view (sekitar line 361-524)
# YANG DIUBAH: Tambahin 'image_id' di dalam dict yang di-append ke data['images']
#
# Cari blok ini di views.py (sekitar line 503-511):
#
#         data['images'].append({
#             'url': image_url,
#             'filename': os.path.basename(img.image.name) if img.image else f'image_{img.id}',
#             'status': img.status,
#             'annotator': img.annotator.email if img.annotator else 'Unassigned',
#             'issue_description': img.issue_description or 'No description',
#             'annotations': annotation_data
#         })
#
# GANTI dengan ini (cuma tambahin baris 'image_id': img.id):
# ============================================================

data['images'].append({
    'image_id': img.id,                                                          # <-- TAMBAHIN BARIS INI
    'url': image_url,
    'filename': os.path.basename(img.image.name) if img.image else f'image_{img.id}',
    'status': img.status,
    'annotator': img.annotator.email if img.annotator else 'Unassigned',
    'issue_description': img.issue_description or 'No description',
    'annotations': annotation_data
})

# ============================================================
# Setelah patch ini di-apply:
# 1. Restart Django (Ctrl+C terus runserver lagi)
# 2. Buka halaman Issue Solving
# 3. Klik "View Issues" → modal kebuka
# 4. Tombol "Mark as Fixed" sekarang ENABLED (warna ijo)
# 5. Klik → confirm dialog → POST ke /finish-image/ → status image jadi 'finished'
# ============================================================
