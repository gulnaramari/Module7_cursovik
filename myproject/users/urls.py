from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import RegisterView, VerifyEmailView,\
    CustomPasswordResetConfirmView, CustomPasswordResetForm, LoginView, LogoutView

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(template_name='users/register.html'), name="register"),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='messenger:home'), name='logout'),
    path('users/verify/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
             form_class=CustomPasswordResetForm,
             template_name='users/registration/password_recovery.html',
             success_url=reverse_lazy('users:password_reset_form')
         ),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
             template_name='users/registration/password_reset_form.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(
             template_name='users/registration/password_reset_confirm.html',
         ),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
             template_name='users/registration/password_new.html'
         ),
         name='password_new'),
]

