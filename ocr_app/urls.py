from django.urls import path
from .views import upload_document, detail

urlpatterns = [
    path('', upload_document, name='upload'),
    path('doc/<int:pk>/', detail, name='detail'),
]