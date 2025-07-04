from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('/about',views.about,name='about'),
     path('/blog_list',views.blog_list,name='blogs')
]