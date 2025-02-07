from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views as dashboard_views

urlpatterns = [
    path('', dashboard_views.dashboard, name='dashboard'),
    path('signin/', dashboard_views.signin, name='signin'),
    # path('logout/', dashboard_views.logoutUser, name='logout'),
    path('exchange/', dashboard_views.exchange, name='exchange'),
    path('profile/', dashboard_views.profile, name='profile'),
    path('market/', dashboard_views.market, name='market'),
    # path('signup/', dashboard_views.signup, name='signup'),
    path('wallet/', dashboard_views.wallet, name='wallet'),
    # path('mpay/', dashboard_views.mpay, name='mpay'),
    path('dt', dashboard_views.mkt_data, name='data'),

    path('api/tickers/', dashboard_views.get_ticker_data, name='get_ticker_data'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
