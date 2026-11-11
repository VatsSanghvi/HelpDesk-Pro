from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number','role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A readable placeholder instead of Django's row of dashes.
        self.fields['role'].choices = [('', 'Choose a role')] + list(User.role_choice)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')