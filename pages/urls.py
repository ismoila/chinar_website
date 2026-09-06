from django.urls import path
from django.contrib.auth import views as auth_views
from pages.views import (
    apply_promo, cancel_order, checkout, discounts_view, homepageview, aboutpageview, locationpageview, update_cart, workerspageview, deliverypageview, ideapageview, categorypageview, servicespageview, send_code_view, verify_code_view, order, review, profile, shopping_cart, logout_view, projectpageview, journal_view, news_view )
from products.views import create_order

app_name = 'pages'   # ← ADD THIS LINE

urlpatterns = [
    path('', homepageview, name='home'),
    path('about/', aboutpageview, name='about'),
    path('address/', locationpageview, name='address'),
    path('designers/', workerspageview, name='designers'),
    path('delivery/', deliverypageview, name='delivery'),
    path('idea/', ideapageview, name='idea'),
    path('category/', categorypageview, name='category'),
    path('services/', servicespageview, name='services'),
    path('cart/', shopping_cart, name='shopping_cart'),
    path('profile/', order, name='order'),
    path('profile_reviews/', review, name='review'),
    path('profile_settings/', profile, name='profile'),
    path('send-code/', send_code_view, name='send_code'),
    path('verify-code/', verify_code_view, name='verify_code'),
    path('logout/', logout_view, name='logout'),
    path('projects/', projectpageview, name='projects'),
    path('checkout/', checkout, name='checkout'),
    path('discounts/', discounts_view, name='discounts'),
    path('journal/', journal_view, name='journal'),
    path('news/', news_view, name='news'),
    # path('projects/', projects_view, name='projects'),
    # path('projects/<int:pk>/', project_detail_view, name='project_detail'),
    # urls.py
path('update-cart/', update_cart, name='update_cart'),
path('create-order/', create_order, name='create_order'),
path('cancel-order/<str:order_id>/', cancel_order, name='cancel_order'),
path('apply-promo/', apply_promo, name='apply_promo'),
]