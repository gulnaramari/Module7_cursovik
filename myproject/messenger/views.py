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
    template_name = 'messenger/list_recipient.html'
    context_object_name = 'recipients'


class RecipientCreateView(generic.CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'messenger/recipient_form.html'
    success_url = reverse_lazy('messenger:list_recipient')


class RecipientUpdateView(generic.UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'messenger/recipient_form.html'
    success_url = reverse_lazy('messenger:list_recipient')


class RecipientDeleteView(generic.DeleteView):
    model = Recipient
    template_name = 'messenger/recipient_confirm_delete.html'
    success_url = reverse_lazy('messenger:list_recipient')


class MessageListView(generic.ListView):
    model = Message
    template_name = 'messenger/message_list.html'
    context_object_name = 'messages'


class MessageCreateView(generic.CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'messenger/message_form.html'
    success_url = reverse_lazy('messenger:message_list')


class MessageUpdateView(generic.UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'messenger/message_form.html'
    success_url = reverse_lazy('messenger:message_list')


class MessageDeleteView(generic.DeleteView):
    model = Message
    template_name = 'messenger/message_confirm_delete.html'
    success_url = reverse_lazy('messenger:message_list')


class MailingListView(generic.ListView):
    model = Mailing
    template_name = 'messenger/list_mailing.html'
    context_object_name = 'mailings'


class MailingCreateView(generic.CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'messenger/mailing_form.html'
    success_url = reverse_lazy('messenger:list_mailing')


class MailingUpdateView(generic.UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'messenger/mailing_form.html'
    success_url = reverse_lazy('messenger:list_mailing')


class MailingDeleteView(generic.DeleteView):
    model = Mailing
    template_name = 'messenger/mailing_confirm_delete.html'
    success_url = reverse_lazy('messenger:list_mailing')


class HomeView(generic.TemplateView):
    template_name = 'messenger/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='Запущена').count()
        context['unique_recipients'] = Recipient.objects.count()
        return context
