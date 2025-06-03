from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils import timezone
from .models import Recipient, Message, Mailing, SendAttempt
from .forms import RecipientForm, MessageForm, MailingForm


# CRUD для получателей (Recipient)

class RecipientListView(generic.ListView):
    model = Recipient
    template_name = 'list_recipient.html'
    context_object_name = 'recipients'


class RecipientCreateView(generic.CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'recipient_form.html'
    success_url = reverse_lazy('list_recipient')


class RecipientUpdateView(generic.UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'recipient_form.html'
    success_url = reverse_lazy('list_recipient')


class RecipientDeleteView(generic.DeleteView):
    model = Recipient
    template_name = 'recipient_confirm_delete.html'
    success_url = reverse_lazy('list_recipient')


# CRUD для сообщений (Message)

class MessageListView(generic.ListView):
    model = Message
    template_name = 'message_list.html'
    context_object_name = 'messages'


class MessageCreateView(generic.CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'message_form.html'
    success_url = reverse_lazy('message_list')


class MessageUpdateView(generic.UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'message_form.html'
    success_url = reverse_lazy('message_list')


class MessageDeleteView(generic.DeleteView):
    model = Message
    template_name = 'message_confirm_delete.html'
    success_url = reverse_lazy('message_list')


class MailingListView(generic.ListView):
    model = Mailing
    template_name = 'list_mailing.html'
    context_object_name = 'mailings'


class MailingCreateView(generic.CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing_form.html'
    success_url = reverse_lazy('list_mailing')


class MailingUpdateView(generic.UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing_form.html'
    success_url = reverse_lazy('list_mailing')


class MailingDeleteView(generic.DeleteView):
    model = Mailing
    template_name = 'mailing_confirm_delete.html'
    success_url = reverse_lazy('list_mailing')


class HomeView(generic.TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='Запущена').count()
        context['unique_recipients'] = Recipient.objects.count()
        return context
