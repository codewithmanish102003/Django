from django.urls import path # type: ignore
from . import views

urlpatterns=[
    path('',views.home,name="home")
    ,path('about/',views.about,name="about")
    ,path('contact/',views.contact,name="contact")
    ,path('services/',views.services,name="services"),
    #dynamic url
    path('services/<int:service_id>/',views.service_details,name='service_details'),
]