from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


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

class AvatarForm(forms.Form):
    avatar = forms.ImageField()
