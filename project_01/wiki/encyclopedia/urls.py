from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("new_page", views.new_page, name="new_page"),
    path("<str:title>", views.entry, name="entry"),
    path("edit/<str:title>", views.edit, name="edit"),
    path('random/', views.random_page, name='random_page'),
    path("error", views.error, name="error")
]
