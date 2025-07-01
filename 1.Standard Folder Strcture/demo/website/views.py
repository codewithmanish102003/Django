from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from .models import Services

def home(request):
    return render(request, 'website/home.html')

def about(request):
    return render(request, 'website/about.html')

def contact(request):
    return render(request, 'website/contact.html')

def services(request):
    services=Services.objects.all
    return render(request, 'website/services.html',{"services":services}) 

def service_details(request,service_id):
    service=get_object_or_404(Services,pk=service_id)
    return render(request,'website/service_details.html',{"service":service})




