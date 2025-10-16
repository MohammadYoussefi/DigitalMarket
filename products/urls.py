from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='products'),
    path('products/<slug:brand_slug>/', views.ProductListView.as_view(), name='product_category'),
    path('product_detail/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:product_id>/rate/', views.RateProductView.as_view(), name='rate_product'),
]