from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views as smartmine_views


urlpatterns = [
    path('', smartmine_views.index, name='home'),
    path("subscribe/", smartmine_views.subscribe, name="subscribe"),
    path('get-price/<str:symbol>/', smartmine_views.get_crypto_price, name='get_crypto_price'),

    # path('prices/', smartmine_views.prices, name='prices'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
