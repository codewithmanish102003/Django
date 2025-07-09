from django.urls import path  # type: ignore

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("books/", views.book_list, name="book_list"),
    path("contact/", views.contact_view, name="contact"),
    path("add_book", views.add_book, name="addbook"),
    path("books/edit/<int:book_id>/", views.edit_book, name="edit_book"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("books/<int:book_id>/", views.book_details, name="book_details"),
]

