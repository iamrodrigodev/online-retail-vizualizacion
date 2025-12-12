from django.contrib import admin
from django.urls import path
from dashboard import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('api/customer-profiles/<str:country>/', views.get_customer_profiles_by_country, name='customer_profiles_by_country'),
    path('api/customer-profiles-global/', views.get_customer_profiles_global, name='customer_profiles_global'),
    path('api/sales-trend/', views.get_sales_trend, name='sales_trend'),
    path('api/top-products/', views.get_top_products, name='top_products'),
    path('api/categories/', views.get_categories, name='get_categories'),
    path('api/client-similarity/compute/', views.compute_client_similarity, name='compute_client_similarity'),
    path('api/client-similarity/customer-ids/', views.get_customer_ids, name='get_customer_ids'),
    path('api/products-by-customers/', views.get_products_by_customers, name='products_by_customers'),
    path('api/sales-detail/<str:date>/', views.get_sales_detail, name='sales_detail'),
]
