from django import forms
from django.contrib.auth.models import User
from . import models
from quiz import models as QMODEL

class StaffUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }

class StaffForm(forms.ModelForm):
    class Meta:
        model=models.Staff
        fields=['address','mobile','profile_pic']

