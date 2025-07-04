from django.shortcuts import render, HttpResponse # type: ignore
from .models import BlogPost

# Create your views here.
def home(request):
    return render(request,'demo/home.html')

def about(request):
    return render(request,"demo/about.html")

def blog_list(request):
    posts=BlogPost.objects.all().order_by('-published_on')
    return render(request,'demo/blog_list.html',{"posts":posts})
