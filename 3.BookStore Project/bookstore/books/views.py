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


#class based views
# from django.contrib import messages
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib.auth.views import LoginView, LogoutView
# from django.urls import reverse_lazy
# from django.views.generic import (
#     ListView, CreateView, UpdateView, DetailView, TemplateView
# )
# from .models import Book
# from .forms import BookForm, ContactForm, RegisterForm

# # Home view
# class HomeView(TemplateView):
#     template_name = 'books/home.html'

# # Book list view
# class BookListView(ListView):
#     model = Book
#     template_name = 'books/book_list.html'
#     context_object_name = 'books'

# # Contact view
# class ContactView(CreateView):
#     template_name = 'books/contact.html'
#     form_class = ContactForm
#     success_url = reverse_lazy('thank_you')

#     def form_valid(self, form):
#         # Process the form data
#         name = form.cleaned_data['name']
#         email = form.cleaned_data['email']
#         message = form.cleaned_data['message']
#         print(f"Name: {name}, Email: {email}, Message: {message}")
#         return super().form_valid(form)

# # Add book view (requires login)
# class AddBookView(LoginRequiredMixin, CreateView):
#     model = Book
#     form_class = BookForm
#     template_name = 'books/add_book.html'
#     success_url = reverse_lazy('book_list')

# # Edit book view (requires login)
# class EditBookView(LoginRequiredMixin, UpdateView):
#     model = Book
#     form_class = BookForm
#     template_name = 'books/edit_book.html'
#     success_url = reverse_lazy('book_list')

#     def form_valid(self, form):
#         messages.success(self.request, "Book updated successfully!")
#         return super().form_valid(form)

# # Book details view
# class BookDetailView(DetailView):
#     model = Book
#     template_name = 'books/book_details.html'
#     context_object_name = 'book'

# # Registration view
# class RegisterView(CreateView):
#     form_class = RegisterForm
#     template_name = 'books/register.html'
#     success_url = reverse_lazy('login')

#     def form_valid(self, form):
#         messages.success(self.request, "Registration successful")
#         return super().form_valid(form)

# # Login view (using Django's built-in LoginView)
# class CustomLoginView(LoginView):
#     template_name = 'books/login.html'
#     success_url = reverse_lazy('book_list')

#     def form_valid(self, form):
#         username = form.cleaned_data.get("username")
#         messages.success(self.request, f"Welcome, {username}!")
#         return super().form_valid(form)

# # Logout view (using Django's built-in LogoutView)
# class CustomLogoutView(LogoutView):
#     template_name = 'books/logout.html'

#     def dispatch(self, request, *args, **kwargs):
#         messages.success(request, "You have been logged out")
#         return super().dispatch(request, *args, **kwargs)