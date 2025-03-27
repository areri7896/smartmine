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
    path('dt', dashboard_views.mkt_data, name='data'),
    path('api/mpesa/callback/', dashboard_views.mpesa_callback, name='mpesa_callback'),
    path('plans/', dashboard_views.investment_plans, name='investment_plans'),
    path('invest/<int:plan_id>/', dashboard_views.invest, name='invest'),
    # path('initiate-investment/', dashboard_views.initiate_investment, name='initiate_investment'),
    path('invest/confirm/<int:plan_id>/', dashboard_views.confirm_investment, name='confirm_investment'),

    path('api/tickers/', dashboard_views.get_ticker_data, name='get_ticker_data'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
