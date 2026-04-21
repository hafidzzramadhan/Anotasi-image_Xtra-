"""
SNIPPET — URL patterns untuk Edit & Delete Job Profile
=====================================================
Buka master/urls.py, cari section comment "# Job Settings" yang udah ada
(sekitar baris 26-28), tambahin 2 baris ini di bawahnya:
"""

# Tambahin di dalam urlpatterns list, di bawah:
#     path('create_job_profile/', ...),
#     path('job-profile/<int:job_id>/', ...),
#     path('upload-job-images/', ...),

path('edit-job-profile/<int:job_id>/', views.edit_job_profile, name='edit_job_profile'),
path('delete-job-profile/<int:job_id>/', views.delete_job_profile, name='delete_job_profile'),


"""
Jadi section Job Settings di urls.py lu akan keliatan kayak gini:

    # Job Settings
    path('create_job_profile/', views.create_job_profile, name='create_job_profile'),
    path('job-profile/<int:job_id>/', views.job_profile_detail, name='job_profile_detail'),
    path('upload-job-images/', views.upload_job_images, name='upload_job_images'),
    path('edit-job-profile/<int:job_id>/', views.edit_job_profile, name='edit_job_profile'),
    path('delete-job-profile/<int:job_id>/', views.delete_job_profile, name='delete_job_profile'),
"""
