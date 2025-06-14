from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.core.mail import send_mail
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import views as auth_views, update_session_auth_hash, login, authenticate
from django.urls import path, reverse_lazy, reverse
from django.utils.decorators import method_decorator

from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import (CreateView, DetailView, FormView, ListView,
                                  TemplateView, UpdateView)

from messenger.views import is_manager

from django.contrib import messages
from .forms import (
    UserRegisterForm, CustomPasswordResetForm, ChangePasswordForm, LoginForm
)
from .models import User
from config.settings import EMAIL_HOST_USER


class RegisterView(CreateView):
    "Регистрация пользователя, отправка письма с токеном подверждения регистрации"
    model = User
    template_name = "users/register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy(
        "users:login"
    )  # Перенаправление на авторизацию после регистрации

    def form_valid(self, form):
        user = form.save(commit=False)
        token = user.generate_verification_token()
        user.is_active = False
        user.save()

        verification_link = f"{settings.DOMAIN}/users/verify/{token}/"
        send_mail(
            "Подтверждение регистрации в сервисе рассылок",
            f"Перейдите по ссылке для подтверждения: {verification_link}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        messages.success(
            self.request, "Письмо с подтверждением отправлено на вашу электронную почту"
        )
        return super().form_valid(form)


class LoginView(FormView):
    "Аутентификация пользователя"
    form_class = LoginForm
    template_name = 'users/login.html'
    success_url = reverse_lazy(
        "messenger:home"
    )  # Перенаправление домой после авторизации

    def get_success_url(self):
        return self.request.POST.get('next', reverse_lazy('messenger:home'))

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            messages.error(self.request, 'Подтвердите ваш адрес электронной почты')
            return redirect('login')
        login(self.request, user)
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy(
        "users:login"
    )  # Перенаправление на авторизацию после выхода


class VerifyEmailView(TemplateView):
    """Подтверждение email по токену"""

    template_name = "users/verify_email.html"

    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)
            user.is_active = True
            user.verification_token = ""
            user.save()
            messages.success(request, "Ваша электронная почта успешно подтверждена.")
            return redirect("users:login")
        except User.DoesNotExist:
            messages.error(request, "Недействительная ссылка подтверждения.")
            return redirect("users:register")


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = "users/password_reset.html"
    success_url = reverse_lazy("users:password_reset_done")
    form_class = CustomPasswordResetForm
    email_template_name = "users/password_reset_email.html"

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

        messages.success(
            self.request,
            "Письмо со ссылкой для смены пароля отправлено на вашу электронную почту",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["domain"] = settings.DOMAIN
        context["protocol"] = "https" if self.request.is_secure() else "http"
        return context


# @method_decorator(never_cache, name='dispatch')
class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    "Установка нового пароля, сброс старого"

    form_class = ChangePasswordForm
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_new")

    def form_valid(self, form):
        if form.errors:
            print("Ошибки формы:", form.errors)
            return self.form_invalid(form)
        with transaction.atomic():
            response = super().form_valid(form)
            update_session_auth_hash(self.request, self.user)
        messages.success(self.request, "Пароль успешно изменён")
        return response


class UserBlockView(LoginRequiredMixin, View):
    """Блокировка пользователя менеджером"""

    def post(self, request, pk):
        if not is_manager(request.user):
            raise Http404("У вас нет прав для выполнения этого действия.")

        user = get_object_or_404(User, id=pk)
        user.is_active = False
        user.save()
        return redirect(reverse("messenger:home"))


class UserUnlockView(LoginRequiredMixin, View):
    """Разблокировка пользователя менеджером"""

    def post(self, request, pk):
        if not is_manager(request.user):
            raise Http404("У вас нет прав для выполнения этого действия.")

        user = get_object_or_404(User, id=pk)
        user.is_active = True
        user.save()
        return redirect(reverse("messenger:home"))


class UserListView(LoginRequiredMixin, ListView):
    """Список пользователей для менеджеров"""

    model = User
    template_name = "users/user_list.html"
    context_object_name = "object_list"

    def get_queryset(self):
        if not is_manager(self.request.user):
            raise Http404("У вас нет прав для просмотра этой страницы.")
        return User.objects.all().order_by("-is_active", "email")
