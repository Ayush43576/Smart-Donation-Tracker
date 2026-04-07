from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('ngos/', views.ngo_list, name='ngo_list'),
    path('ngos/<int:ngo_id>/', views.ngo_detail, name='ngo_detail'),
    path('donate/', views.donate, name='donate'),
    path('donate/<int:ngo_id>/', views.donate, name='donate_to'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
