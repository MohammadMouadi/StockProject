from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('stock/<str:symbol>/', views.single_stock, name='single_stock'),
	path('historic/<str:symbol>/', views.single_stock_historic, name='single_stock_historic'),
	path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
	path('accounts/logout/', views.logout_view, name='logout'),
	path('accounts/register/', views.register, name='register'),
	path('accounts/myaccount/',views.my_account,name='my_account'),
	path('accounts/myaccount/updatemyaccount',views.update_my_account,name ='update_my_account'),
	path('trade/', views.trade, name='trade'),
	path('compare/', views.compare, name='compare'),
	path('topbuysell', views.TopBuySellListView.as_view(), name='top_buy_sell'),]