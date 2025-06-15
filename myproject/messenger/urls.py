from django.urls import path

from .apps import MessengerConfig
from . import views
from .views import HomeView, RecipientListView, RecipientCreateView, RecipientUpdateView, RecipientDeleteView, \
    MessageListView, MessageCreateView, MessageUpdateView, MessageDeleteView, MessageDetailView, MailingListView, \
    MailingCreateView, MailingUpdateView, MailingDeleteView, MailingDetailView, MailingDeactivateView, \
    MailingStatistView

app_name = MessengerConfig.name

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('recipients/', RecipientListView.as_view(), name='list_recipient'),
    path('recipients/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/update/<int:pk>/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/delete/<int:pk>/', RecipientDeleteView.as_view(), name='recipient_delete'),
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/update/<int:pk>/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('mailings/', MailingListView.as_view(), name='list_mailing'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/update/<int:pk>/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/delete/<int:pk>/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/<int:pk>/deactivate/', MailingDeactivateView.as_view(), name='mailing_deactivate'),
    path("send_mailing/", views.send_mailing, name="send_mailing"),
    path("mailing_reports/", views.mailing_reports, name="mailing_reports"),
    path("stats/", MailingStatistView.as_view(), name="mailing_statist")

    ]
