from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views as smartmine_views


urlpatterns = [
    path('', smartmine_views.index, name='home'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
