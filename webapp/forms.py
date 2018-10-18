from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import GroupAccount


class SignUpForm(UserCreationForm):
    username = forms.RegexField(regex=r'^[\w]+$',
                                max_length=30,
                                error_messages={'invalid': "This value may contain only letters, numbers and _ characters."})
    email = forms.EmailField(max_length=50, help_text='Required. Inform a valid email address.')
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError("This email address is already in use. Please supply a different email address.")
        return self.cleaned_data['email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        username_qs1 = User.objects.filter(username__iexact=username)
        username_qs2 = GroupAccount.objects.filter(name__iexact=username)
        if username_qs1.exists() or username_qs2.exists():
            raise ValidationError("Username already exists")
        return username

class AvatarForm(forms.Form):
    avatar = forms.ImageField()
