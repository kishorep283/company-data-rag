from django.urls import path

from .views import PDFUploadView


urlpatterns = [
	path("documents/upload/", PDFUploadView.as_view(), name="documents-upload"),
]
