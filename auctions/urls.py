from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_new, name="create"),
    path("<str:title>", views.listing, name="listing"),
    path("watchlist/<str:title>", views.watchlist, name="watchlist"),
    path("remove_watch/<str:title>", views.remove_watch, name="remove_watch")
]
