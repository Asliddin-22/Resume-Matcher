from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("jobs/", views.browse_jobs, name="browse_jobs"),
    path("jobs/<str:job_id>/", views.job_detail, name="job_detail"),
]
