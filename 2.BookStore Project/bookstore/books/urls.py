from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
]
