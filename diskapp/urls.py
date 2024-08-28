from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("files/", views.files_list, name="files_list"),
    path("download/", views.download_file, name="download_file"),
]
