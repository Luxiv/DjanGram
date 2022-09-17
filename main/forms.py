from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError
from .models import Article, UserAccount
from .utils import send_email_for_verify


class NewPostForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'is_published', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 60, 'rows': 10}),
        }


class RegistrationUserForm(UserCreationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email address',
                             widget=forms.TextInput(attrs={'class': 'form-input', 'autocomplete': 'email'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = UserAccount
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if not self.user_cache.email_verify:
                send_email_for_verify(self.request, self.user_cache)
                raise ValidationError(' Email not verify? check your email', code='invalid_login')
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class FullProfileInfoForm(forms.ModelForm):
    email = forms.EmailField(label='Email address',
                             widget=forms.TextInput(attrs={'class': 'form-input', 'autocomplete': 'email'}))

    class Meta:
        model = UserAccount
        fields = ['first_name', 'last_name', 'avatar', 'birth', 'about_user', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'about_user': forms.Textarea(attrs={'cols': 60, 'rows': 10}),

        }
