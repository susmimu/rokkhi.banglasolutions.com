# ----------------------------------------------------------------------------------------------
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.forms.fields import EmailField
from django.forms.forms import Form
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from . models import Profile
from app_devices.models import ImageCaptureCommand
# ----------------------------------------------------------------------------------------------


# **********************************************************************************************
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'birth_date', 'city', 'country']
# **********************************************************************************************


# **********************************************************************************************
class SignMeUpForm(UserCreationForm):
    # ----------------------------------------------------------------------------------------------
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'required': 'required',
        'autofocus': True,
        # 'readonly': 'readonly',
        # 'help_texts': 'Valid mobile no only',
        'id': 'id_username',
        # 'type': 'text',
        # 'min_length': 5,
        # 'max_length': 150,
        'placeholder': 'User name',
        'name': 'username',
        'error_messages': 'Please enter your User name',
        # 'style': 'background-color: #f8f9fa; border-color: #f8f9fa; border-radius: 0; border: none;',
        'style': 'border-radius: 3;',
    }))
    username.label = 'User name'
    # ----------------------------------------------------------------------------------------------
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control mb-3',
        'required': 'required',
        'autofocus': False,
        # 'readonly': 'readonly',
        'id': 'id_email',
        # 'type': 'text',
        # 'min_length': 5,
        # 'max_length': 150,
        'placeholder': 'Email address',
        'name': 'email',
        'error_messages': 'Please enter your email',
        # 'style': 'background-color: #f8f9fa; border-color: #f8f9fa; border-radius: 0; border: none;',
        'style': 'border-radius: 3;',
    }))
    email.label = 'Email address'
    # ----------------------------------------------------------------------------------------------
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3',
        'required': 'required',
        'autofocus': False,
        # 'readonly': 'readonly',
        'id': 'id_password1',
        # 'type': 'text',
        # 'min_length': 5,
        # 'max_length': 150,
        'placeholder': 'Password',
        'name': 'password1',
        'error_messages': 'Please enter your password',
        # 'style': 'background-color: #f8f9fa; border-color: #f8f9fa; border-radius: 0; border: none;',
        'style': 'border-radius: 3;',
    }))
    password1.label = 'Password'
    # ----------------------------------------------------------------------------------------------
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3',
        'required': 'required',
        'autofocus': False,
        # 'readonly': 'readonly',
        'id': 'id_password2',
        # 'type': 'text',
        # 'min_length': 5,
        # 'max_length': 150,
        'placeholder': 'Confirm password',
        'name': 'password2',
        'error_messages': 'Please confirm your password',
        # 'style': 'background-color: #f8f9fa; border-color: #f8f9fa; border-radius: 0; border: none;',
        'style': 'border-radius: 3;',
    }))
    password2.label = 'Confirm password'
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    # ----------------------------------------------------------------------------------------------
# **********************************************************************************************


# **********************************************************************************************
class SignMeInForm(forms.Form):
    # ----------------------------------------------------------------------------------------------
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'required': 'required',
        'autofocus': True,
        # 'readonly': 'readonly',
        'help_texts': 'Valid username',
        # 'id': 'id_username',
        # 'type': 'text',
        # 'min_length': 5,
        # 'max_length': 150,
        'placeholder': 'User name',
        'name': 'username',
        'error_messages': 'Please enter User name',
        # 'style': 'background-color: #f8f9fa; border-color: #f8f9fa; border-radius: 0; border: none;',
        # 'style': 'border-radius: 3;',
    }))
    username.label = 'Mobile no'
    # ----------------------------------------------------------------------------------------------
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3',
        'required': 'required',
        'autofocus': False,
        # 'readonly': 'readonly',
        'help_texts': 'Valid password',
        # 'id': 'id_password',
        # 'type': 'text',
        # 'min_length': 5,
        # 'max_length': 150,
        'placeholder': 'Password',
        'name': 'password',
        'error_messages': 'Please enter password',
        # 'style': 'background-color: #f8f9fa; border-color: #f8f9fa; border-radius: 0; border: none;',
        # 'style': 'border-radius: 3;',
    }))
    password.label = 'Password'
    # ----------------------------------------------------------------------------------------------
# **********************************************************************************************


# **********************************************************************************************
class AvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        # fields = '__all__'
        # exclude = ['user']
# **********************************************************************************************


# **********************************************************************************************
class ChangeMyPasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ----------------------------------------------------------------------------------
        self.fields['old_password'].widget.attrs.update({
            "class": "form-control form-floating mt-2 mb-4",
            "autofocus": True,
            "required": True,
            "style": "color: black; max-width: 100%;",
            "placeholder": "Old password",
        })
        self.fields['old_password'].label = 'Old password'
        # ----------------------------------------------------------------------------------
        self.fields['new_password1'].widget.attrs.update({
            "class": "form-control form-floating mt-2 mb-0",
            "autofocus": False,
            "required": True,
            "style": "color: black; max-width: 100%;",
            "placeholder": "New password",
        })
        self.fields['new_password1'].label = 'New password'
        # ----------------------------------------------------------------------------------
        self.fields['new_password2'].widget.attrs.update({
            "class": "form-control form-floating mt-2 mb-4",
            "autofocus": False,
            "required": True,
            "style": "color: black; max-width: 100%;",
            "placeholder": "Confirm new password",
        })
        self.fields['new_password2'].label = 'Confirm new password'
        # ----------------------------------------------------------------------------------
# **********************************************************************************************


# **********************************************************************************************
class ExcelToContactForm(forms.Form):
    # ----------------------------------------------------------------------------------------------
    excel_file_form = forms.FileField(widget=forms.FileInput(attrs={
        'class': 'form-control',
        'required': 'required',
        'autofocus': False,
        # 'readonly': 'readonly',
        # 'help_texts': 'Valid mobile no',
        'id': 'id_excel_file_form',
        'type': 'file',
        # 'min_length': 5,
        # 'max_length': 150,
        # 'placeholder': 'Mobile no',
        'name': 'excel_file_form',
        # 'error_messages': 'Please enter your mobile number',
        # 'style': 'background-color: #f8f9fa; border-color: #f8f9fa; border-radius: 0; border: none;',
        'style': 'border-radius: 3;',
    }))
    excel_file_form.label = ''
    # ----------------------------------------------------------------------------------------------
# **********************************************************************************************


# **********************************************************************************************
class ForgotPasswordForm(forms.Form):
    # ----------------------------------------------------------------------------------------------
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control mb-3',
        'required': 'required',
        'autofocus': True,
        # 'readonly': 'readonly',
        'help_texts': 'Valid mobile no only',
        'id': 'id_username',
        # 'type': 'text',
        # 'min_length': 5,
        # 'max_length': 150,
        'placeholder': 'Mobile no',
        'name': 'username',
        'error_messages': 'Please enter your mobile number',
        # 'style': 'background-color: #f8f9fa; border-color: #f8f9fa; border-radius: 0; border: none;',
        'style': 'border-radius: 3;',
    }))
    username.label = 'Mobile no'
    # ----------------------------------------------------------------------------------------------
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control mb-3',
        'required': 'required',
        'autofocus': False,
        # 'readonly': 'readonly',
        'id': 'id_email',
        # 'type': 'text',
        # 'min_length': 5,
        # 'max_length': 150,
        'placeholder': 'Email address',
        'name': 'email',
        'error_messages': 'Please enter your email',
        # 'style': 'background-color: #f8f9fa; border-color: #f8f9fa; border-radius: 0; border: none;',
        'style': 'border-radius: 3;',
    }))
    email.label = 'Email address'
    # ----------------------------------------------------------------------------------------------
# **********************************************************************************************


# **********************************************************************************************
class RecoverPasswordForm(forms.Form):
    # ----------------------------------------------------------------------------------------------
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3',
        'required': 'required',
        'autofocus': False,
        # 'readonly': 'readonly',
        'id': 'id_password1',
        # 'type': 'text',
        # 'min_length': 5,
        # 'max_length': 150,
        'placeholder': 'Password',
        'name': 'password1',
        'error_messages': 'Please enter your password',
        # 'style': 'background-color: #f8f9fa; border-color: #f8f9fa; border-radius: 0; border: none;',
        'style': 'border-radius: 3;',
    }))
    password1.label = 'Password'
    # ----------------------------------------------------------------------------------------------
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-3',
        'required': 'required',
        'autofocus': False,
        # 'readonly': 'readonly',
        'id': 'id_password2',
        # 'type': 'text',
        # 'min_length': 5,
        # 'max_length': 150,
        'placeholder': 'Confirm password',
        'name': 'password2',
        'error_messages': 'Please confirm your password',
        # 'style': 'background-color: #f8f9fa; border-color: #f8f9fa; border-radius: 0; border: none;',
        'style': 'border-radius: 3;',
    }))
    password2.label = 'Confirm password'
# **********************************************************************************************
