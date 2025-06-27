from django.http import HttpResponse
from django.shortcuts import render

from .models import BlogPost

# def hello(request):
#     return HttpResponse("<h1>Hello Django!</h1>")

def about(request):
    return HttpResponse("<h2>This is about page</h2>")

def contact(request):
    return HttpResponse("<h2>This is contact page</h2>")

#url parameters
def greet(request,name):
    return HttpResponse(f"<h2>Hello {name.title()}! </h2>")

#templates
def hello(request):
    return render(request,"mysite/hello.html")

def blog_list(request):
    posts = BlogPost.objects.all().order_by('-published_on')  # fixed typo
    return render(request, 'mysite/bloglist.html', {'posts': posts})
