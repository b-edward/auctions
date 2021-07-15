from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_new, name="create"),
    path("<str:title>/$", views.listing, name="listing"),   # /$ to terminate url pattern
    path("watchlist_add/<str:title>", views.watchlist_add, name="watchlist_add"),
    path("watchlist_remove/<str:title>", views.watchlist_remove, name="watchlist_remove"),
    path("watchlist_view", views.watchlist_view, name="watchlist_view"),
    path("bid/<str:title>", views.bid, name="bid"),
    path("close/<str:title>", views.close, name="close"),
    path("closed", views.closed, name="closed")
]
