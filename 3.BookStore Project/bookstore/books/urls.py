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
    path("books/delete/<int:book_id>/", views.delete_book, name="delete_book"),
    path("profile/", views.profile, name="profile"),
]


#class based Views
# from django.urls import path
# from . import views

# urlpatterns = [
#     path("", views.HomeView.as_view(), name="home"),
#     path("books/", views.BookListView.as_view(), name="book_list"),
#     path("contact/", views.ContactView.as_view(), name="contact"),
#     path("add_book/", views.AddBookView.as_view(), name="addbook"),
#     path("books/edit/<int:pk>/", views.EditBookView.as_view(), name="edit_book"),
#     path("books/<int:pk>/", views.BookDetailView.as_view(), name="book_details"),
#     path("register/", views.RegisterView.as_view(), name="register"),
#     path("login/", views.CustomLoginView.as_view(), name="login"),
#     path("logout/", views.CustomLogoutView.as_view(), name="logout"),
# ]