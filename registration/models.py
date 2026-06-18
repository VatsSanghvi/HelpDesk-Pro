from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, first_name, last_name, email, password, **extra_fields):
        """
        Create and save a User with the given first name, last name, email and password.
        """
        if not first_name:
            raise ValueError('Users must have a first name')
        if not last_name:
            raise ValueError('Users must have a last name')
        if not email:
            raise ValueError('Users must have an email address')
        
        user = self.model(
            email = self.normalize_email(email), 
            first_name = self.normalize_email(first_name),
            last_name = self.normalize_email(last_name),
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given first name, last name, email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(first_name, last_name, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    role_choice = (
        ("Admin","Admin"),
        ("Manager","Manager"),
        ("Viewer","Viewer")
    )
    
    email           = models.EmailField(_('Email Address'), max_length=255, unique=True)
    first_name      = models.CharField(_('First Name'), max_length=30)
    last_name       = models.CharField(_('Last Name'), max_length=30)
    phone_number    = models.CharField(_("Phone Number"), max_length=10,null=True,blank=True)
    is_active       = models.BooleanField(_('Active'), default=True)
    is_staff        = models.BooleanField(_('Staff'), default=False)
    date_joined     = models.DateTimeField(_('Date Joined'), default=timezone.now)
    role = models.CharField(_("Role"), max_length=50,choices=role_choice,null=True,blank=True)
    


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = self.first_name + ' ' + self.last_name
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def get_absolute_url(self):
        return reverse("user_detail", kwargs={"pk": self.pk})
