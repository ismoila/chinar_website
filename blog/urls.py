from django.urls import path
from .views import blog_list_view, blog_detail_view

app_name = 'blog'

urlpatterns = [
    path('', blog_list_view, name='post_list'),
    path('<slug:slug>/', blog_detail_view, name='post_detail'),
]