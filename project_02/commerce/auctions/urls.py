from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('listing', views.listing, name='listing'),
    path('listing/<int:listing_id>/', views.listing_detail, name='listing_detail'),
    path('listing/<int:listing_id>/add_to_watchlist/', views.add_to_watchlist, name='add_to_watchlist'),
    path('listing/<int:listing_id>/remove_from_watchlist/', views.remove_from_watchlist, name='remove_from_watchlist'),
    path('listing/<int:listing_id>/bid/', views.bid_listing, name='bid_listing'),
    path('listing/<int:listing_id>/close/', views.close_listing, name='close_listing'),
    path('listing/<int:listing_id>/comment/', views.add_comment, name='add_comment'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),

]
