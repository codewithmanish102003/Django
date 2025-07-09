from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render  # type: ignore

from .forms import BookForm, ContactForm, RegisterForm
from .models import Book


def home(request):
    return render(request, 'books/home.html')

def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})

def contact_view(request):
    form = ContactForm()
    
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            # Process data (e.g., send email or save)
            print(f"Name: {name}, Email: {email}, Message: {message}")
            return render(request, 'books/thank_you.html', {'name': name})

    return render(request, 'books/contact.html', {'form': form})

@login_required
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'books/add_book.html', {'form': form})

@login_required
def edit_book(request, book_id):
    book = Book.objects.get(pk=book_id)
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'books/edit_book.html', {'form': form, 'book': book})

def register_view(request):
    if request.method == "POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registeration successful")
            return redirect('login')
        
    else:
        form=RegisterForm()

    return render(request,'books/register.html',{'form':form})

def login_view(request):
    if request.method == "POST":
        form=AuthenticationForm(request,data=request.POST)

        if form.is_valid():
            username=form.cleaned_data.get("username")
            password=form.cleaned_data.get("password")

            user=authenticate(username=username,password=password)

            if user is not None:
                login(request,user)
                messages.success(request,f"welcome, {username}!")
                return redirect('book_list')
            else:
                messages.error(request,"Invalid Credentials")

    else:
        form=AuthenticationForm()

    return render(request,'books/login.html',{'form':form})
    

def logout_view(request):
    logout(request)
    messages.success(request,"You have been logged out")

    return redirect('login')

def book_details(request, book_id):
    book = Book.objects.get(pk=book_id)
    return render(request, 'books/book_details.html', {'book': book})
