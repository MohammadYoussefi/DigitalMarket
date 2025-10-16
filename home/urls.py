from django import urls
from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('<slug:brand_slug>/', views.HomeView.as_view(), name='home_by_brand'),
    path('home/contact_us/', views.ContactView.as_view(), name='contact_us'),
    path('home/search/', views.SearchView.as_view(), name='search'),
]