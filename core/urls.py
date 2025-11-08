from django.contrib import admin
from django.urls import path
from dashboard import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('api/customer-profiles/<str:country>/', views.get_customer_profiles_by_country, name='customer_profiles_by_country'),
    path('api/sales-trend/', views.get_sales_trend, name='sales_trend'),
]
