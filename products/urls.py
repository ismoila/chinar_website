from django.urls import path
from products.views import add_to_cart, buy_now, product_options, callback_request, one_click_order, clear_recent_searches, remove_recent_search, remove_from_cart, reply_review, review_vote, search_dropdown_data, search_results, search_suggest, update_cart, wishlistPageView, wishlist_toggle, category_detail, product_detail_view

app_name = "products"
urlpatterns = [
    path("product/<slug:slug>/", product_detail_view, name="product_detail"),
    path("wishlist/", wishlistPageView, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", wishlist_toggle, name="wishlist_toggle"),
    path('category/<int:pk>/', category_detail, name='category_detail'),
    path('review/<int:review_id>/vote/<str:vote_type>/', review_vote, name='review_vote'),
    path('review/<int:review_id>/reply/', reply_review, name='reply_review'),
    path("<int:pk>/add_to_cart/<int:quantity>/", add_to_cart, name="add_to_cart"),
    path("update_cart/", update_cart, name="update_cart"),
    path("remove_from_cart/<int:pk>/", remove_from_cart, name="remove_from_cart"),
    path('search/', search_results, name='search_results'),
    path('search/suggest/', search_suggest, name='search_suggest'),
    path('search/dropdown-data/', search_dropdown_data, name='search_dropdown_data'),
    path('search/clear-recent/', clear_recent_searches, name='clear_recent_searches'),
    path('search/remove-recent/', remove_recent_search, name='remove_recent_search'),
    path('callback/', callback_request, name='callback_request'),
    path('one-click/', one_click_order, name='one_click_order'),
    path('<int:pk>/buy-now/', buy_now, name='buy_now'),
    path('<int:pk>/options/', product_options, name='product_options'),
]