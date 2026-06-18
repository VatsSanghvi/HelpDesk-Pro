from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, DetailView, 
    CreateView, UpdateView, DeleteView,
)
from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin

# FORM
from .forms import CustomUserCreationForm

# DECORATORS
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .decorators import admin_required, my_user_details

@login_required
def home(request):
    context = {}
    return render(request, 'registration/home.html', context)

# USER CBV
@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class UserListView(LoginRequiredMixin, ListView):
    model = User
    # default context = model_list
    # default template = app_name/model_list.html
    # default query = model.objects.all()

@method_decorator(login_required, name='dispatch')
@method_decorator(admin_required, name='dispatch')
class UserRoleListView(LoginRequiredMixin, ListView):
    model = User
    # default context = model_list
    # default template = app_name/model_list.html
    # default query = model.objects.all()
    def get_queryset(self):
        return User.objects.filter(role=self.kwargs['role'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role'] = self.kwargs['role']
        return context

@method_decorator(my_user_details, name='dispatch')
class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'user_details'

@method_decorator(admin_required, name='dispatch')
class UserCreateView(LoginRequiredMixin, CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/user_form.html'

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name')