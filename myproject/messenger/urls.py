from django.urls import path

from .apps import MessengerConfig
from .views import (
    HomeView, RecipientListView, RecipientCreateView, RecipientUpdateView,
    RecipientDeleteView, MessageListView, MessageCreateView, MessageUpdateView,
    MessageDeleteView, MailingListView, MailingCreateView, MailingUpdateView,
    MailingDeleteView, SendMailingView
)

app_name = MessengerConfig.name

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('recipients/', RecipientListView.as_view(), name='list_recipient'),
    path('recipients/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/update/<int:pk>/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipients/delete/<int:pk>/', RecipientDeleteView.as_view(), name='recipient_delete'),
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('messages/update/<int:pk>/', MessageUpdateView.as_view(), name='message_update'),
    path('messages/delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),
    path('mailings/', MailingListView.as_view(), name='list_mailing'),
    path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/update/<int:pk>/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/delete/<int:pk>/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('send-mailing/<int:mailing_id>/', SendMailingView.as_view(), name='send_mailing'),
    ]
