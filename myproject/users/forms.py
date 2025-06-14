from django import forms
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm, UserCreationForm)

from .models import User


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(max_length=35, required=True)
    usable_password = None

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "phone",
            "avatar",
            "country",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите ваш email"}
        )
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите ваш логин"}
        )
        self.fields["phone"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите ваш номер телефона"}
        )
        self.fields["avatar"].widget.attrs.update(
            {
                "class": "form-control",
            }
        )
        self.fields["country"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите вашу страну"}
        )
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите ваш пароль"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Повторите ваш пароль"}
        )

    def cleane_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if phone and not phone.isdigit():
            raise forms.ValidationError("Введите верный номер телефона")


class CustomPasswordResetForm(PasswordResetForm):
    "Форма сброса пароля"

    class Meta:
        model = User
        fields = ("email",)


class ChangePasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["new_password1"].widget.attrs.update({"class": "form-control"})
        self.fields["new_password2"].widget.attrs.update({"class": "form-control"})


class LoginForm(AuthenticationForm):
    "Форма входа с email"

    username = forms.EmailField(label="Email")
