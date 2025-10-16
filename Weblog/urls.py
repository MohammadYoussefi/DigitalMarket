from django.urls import path
from . import views

app_name = 'Weblog'

urlpatterns = [
    path('view_blogpost/', views.WeblogView.as_view(), name='view_weblog'),
    path('view_post/<slug:post_slug>/', views.BlogPostView.as_view(), name='view_post'),
]