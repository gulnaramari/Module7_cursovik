from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import RegisterView, LoginView, UserLogoutView, CustomPasswordResetConfirmView, CustomPasswordResetForm, \
    UserBlockView, UserUnlockView, UserListView, VerifyEmailView

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(template_name='users/register.html'), name="register"),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('users/verify/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
             form_class=CustomPasswordResetForm,
             template_name='users/password_recovery.html',
             success_url=reverse_lazy('users:password_reset_form'),
             email_template_name="users/password_reset_email.html",
             ),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_form.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
         ),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_new.html'
         ),
         name='password_new'),
    path("block/<int:pk>/", UserBlockView.as_view(), name="block_user"),
    path("unblock/<int:pk>/", UserUnlockView.as_view(), name="unblock_user"),
    path("users/", UserListView.as_view(), name="user_list"),

]


