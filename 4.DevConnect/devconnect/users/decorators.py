from django.contrib.auth.decorators import login_required as django_login_required
from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps


def login_required(view_func):
    """
    Custom login required decorator that redirects to our custom login URL.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('users:login')
    return wrapper


def login_required_mixin(view_func):
    """
    Alternative decorator that can be used as a mixin.
    """
    return login_required(view_func)
