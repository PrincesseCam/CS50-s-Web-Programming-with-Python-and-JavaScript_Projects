from django.urls import path
from . import views

urlpatterns = [
    # Homepage showing active listings
    path("", views.index, name="index"),

    # User authentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),

    # Listing-specific pages
    path("listing/<int:id>/", views.listingDetail, name="listingDetail"),
    path("listing/<int:listing_id>/close/", views.close_listing, name="close_listing"),
    path("listing/<int:listing_id>/add_watchlist/", views.add_to_watchlist, name="add_watchlist"),
    path("listing/<int:listing_id>/remove_watchlist/", views.remove_from_watchlist, name="remove_watchlist"),

    path("create/", views.createListing, name="create"),

    # Watchlist
    path("watchlist/", views.watchlist, name="watchlist"),

    # Categories
    path("categories/", views.categoriesListing, name="categoriesListing"),
    path('categories/<str:category_id>/', views.category_items, name='category_items'),
    
]
