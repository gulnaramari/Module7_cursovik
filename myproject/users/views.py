from django.contrib.auth import login
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.views.generic import (
    CreateView, FormView, UpdateView,
    DetailView, TemplateView
)
from django.contrib.auth.views import (
    PasswordResetConfirmView,
    LogoutView,
)
from django.contrib import messages
from .forms import (
    UserRegisterForm, LoginForm,
    CustomPasswordResetForm, ChangePasswordForm
)
from .models import User
from config.settings import EMAIL_HOST_USER


class RegisterView(CreateView):
    "Регистрация пользователя, отправка письма с токеном подверждения регистрации"
    model = User
    template_name = "register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def send_welcome_email(self, user_email):
        subject = 'Добро пожаловать в наш сервис'
        message = 'Спасибо, что зарегистрировались в нашем сервисе!'
        from_email = EMAIL_HOST_USER
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)


class LoginView(FormView):
    "Аутентификация пользователя"
    form_class = LoginForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('messenger:list_recipient')

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
           messages.error(self.request, 'Подтвердите ваш адрес электронной почты')
           return redirect('login')
        return super().form_valid(form)


class LogoutView(LogoutView):
    "Выход из системы"
    next_page = reverse_lazy('messenger:home')


class VerifyEmailView(TemplateView):
    """Подтверждение email по токену"""
    template_name = 'users/registration/verify_email.html'

    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)
            user.is_active = True
            user.verification_token = ''
            user.save()
            messages.success(request, 'Ваша электронная почта успешно подтверждена.')
            return redirect('users:login')
        except User.DoesNotExist:
            messages.error(request, 'Недействительная ссылка подтверждения.')
            return redirect('users:register')


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'users/registration/password_reset.html'
    success_url = reverse_lazy('users:password_reset_done')
    form_class = CustomPasswordResetForm

    def form_valid(self, form):
        user = form.save(commit=False)
        token = user.generate_verification_token()

        verification_link = f"{settings.DOMAIN}/users/verify/{token}/"
        send_mail(
            "Восстановление пароля",
            f"Перейдите по ссылке для смены пароля: {verification_link}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        messages.success(self.request, 'Письмо со ссылкой для смены пароля отправлено на вашу электронную почту')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    "Установка нового пароля, сброс старого"
    form_class = ChangePasswordForm
    template_name = 'users/registration/password_reset_confirm.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Пароль успешно изменён')
        return response