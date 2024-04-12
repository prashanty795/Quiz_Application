from django import forms
from django.contrib.auth.models import User
from . import models

class ManagerUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }

class ManagerForm(forms.ModelForm):
    class Meta:
        model=models.Manager
        fields=['address','mobile','profile_pic']

