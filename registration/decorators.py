from django.shortcuts import redirect
from django.contrib import messages
from vats.models import Ticket
from registration.models import User

def logout_required(my_function):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return my_function(request, *args, **kwargs)
        else:
            return redirect('/')
    return wrapper

def admin_required(my_function):
    def wrapper(request, *args, **kwargs):
        if request.user.role == "Admin":
            return my_function(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not allowed to access this page.')
            return redirect('home')
    return wrapper

def manager_required(my_function):
    def wrapper(request, *args, **kwargs):
        if request.user.role == "Manager":
            return my_function(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not allowed to access this page.')
            return redirect('home')
    return wrapper

def viewer_required(my_function):
    def wrapper(request, *args, **kwargs):
        if request.user.role == "Viewer":
            return my_function(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not allowed to access this page.')
            return redirect('home')
    return wrapper

def viewer_required_only(my_function):
    def wrapper(request, *args, **kwargs):
        if request.user.role == "Viewer" and request.user.id == kwargs['id']:
            return my_function(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not allowed to access this page.')
            return redirect('home')
    return wrapper

def viewernotallowed(my_function):
    def wrapper(request, *args, **kwargs):
        print(kwargs)
        ticket = Ticket.objects.get(id=kwargs['id'])
        if request.user.role == "Admin" or ticket.assigned_to.id == request.user.id:
            return my_function(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not allowed to access this page.')
            return redirect('home')
    return wrapper

def adminnotallowed(my_function):
    def wrapper(request, *args, **kwargs):
        print(kwargs)
        ticket = Ticket.objects.get(id=kwargs['id'])
        if request.user.role == "Viewer" or ticket.assigned_to.id == request.user.id:
            return my_function(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not allowed to access this page.')
            return redirect('home')
    return wrapper


def my_user_details(my_function):
    def wrapper(request, *args, **kwargs):
        # ticket = Ticket.objects.get(id=kwargs['id'])
        # if ticket.assigned_to.id == request.user.id or request.user.role == "Admin" or ticket.created_by.id == request.user.id:
            # do something.
        if request.user.role == "Admin" or request.user.id == kwargs['pk']:
            return my_function(request, *args, **kwargs)
        else:
            messages.warning(request, 'You are not allowed to access this page.')
            return redirect('home')
    return wrapper