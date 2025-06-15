from pyexpat.errors import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import generic, View
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils import timezone
from django.views.generic import DetailView, TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from .models import Recipient, Message, Mailing, SendAttempt
from .forms import RecipientForm, MessageForm, MailingForm
from django.contrib.auth import get_user
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .service import get_mailing_statistics, send_mailing, is_manager


class RecipientListView(LoginRequiredMixin, generic.ListView):
    model = Recipient
    template_name = 'messenger/list_recipient.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        if is_manager(self.request.user):
            queryset = Recipient.objects.all()
        else:
            queryset = Recipient.objects.filter(owner=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipients'] = self.get_queryset()
        return context

    # @method_decorator(cache_page(60 * 5, key_prefix='client_list'))
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)


class RecipientCreateView(LoginRequiredMixin, generic.CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'messenger/recipient_form.html'
    success_url = reverse_lazy('messenger:list_recipient')

    def form_valid(self, form):
        """Присваиваем авторизованного пользователя создаваемому получателю"""
        user = get_user(self.request)
        form.instance.owner = user
        form.instance.save()
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'messenger/recipient_update.html'

    success_url = reverse_lazy('messenger:list_recipient')
    context_object_name = 'recipient'

    def get_object(self, queryset=None):
        recipient = get_object_or_404(Recipient, pk=self.kwargs.get('pk'))
        if recipient.owner is None:
            raise PermissionDenied('У этого получателя не установлен владелец.')
        if is_manager(self.request.user) and recipient.owner != self.request.user:
            raise PermissionDenied('Менеджеры не имеют прав на редактирование чужих получателей')
        if not is_manager(self.request.user) and recipient.owner != self.request.user:
            raise PermissionDenied('У вас нет прав на редактирование этого получателя')
        return recipient

    def form_valid(self, form):
        form.instance.save()
        return super().form_valid(form)


class RecipientDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Recipient
    template_name = 'messenger/recipient_confirm_delete.html'
    success_url = reverse_lazy('messenger:list_recipient')

    def get_object(self, queryset=None):
        recipient = get_object_or_404(Recipient, pk=self.kwargs.get('pk'))
        if not is_manager(self.request.user) and recipient.owner != self.request.user:
            raise PermissionDenied('У вас нет прав на удаление этого получателя')
        if is_manager(self.request.user) and recipient.owner != self.request.user:
            raise PermissionDenied('Менеджеры не могут удалять чужих получателей')
        return recipient


class MessageListView(LoginRequiredMixin, generic.ListView):
    model = Message
    template_name = 'messenger/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        if is_manager(self.request.user):
            return Message.objects.all()
        else:
            return Message.objects.filter(owner=self.request.user)

    # @method_decorator(cache_page(60 * 5, key_prefix="messages:list"))
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)


class MessageCreateView(LoginRequiredMixin, generic.CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'messenger/message_form.html'
    success_url = reverse_lazy('messenger:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.object = form.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'messenger/message_form.html'
    success_url = reverse_lazy('messenger:message_list')

    def get_object(self, queryset=None):
        message = get_object_or_404(Message, pk=self.kwargs['pk'])
        if message.owner != self.request.user:
            raise PermissionDenied("Вы не можете редактировать это сообщение.")
        return message


class MessageDeleteView(generic.DeleteView):
    model = Message
    template_name = 'messenger/message_confirm_delete.html'
    success_url = reverse_lazy('messenger:message_list')

    def get_object(self, queryset=None):
        message = get_object_or_404(Message, pk=self.kwargs['pk'])
        if message.owner != self.request.user:
            raise PermissionDenied("Вы не можете удалять это сообщение.")
        return message


class MessageDetailView(DetailView):
    model = Message
    template_name = 'mail_messages/message_detail.html'
    context_object_name = 'message'


@login_required
def send_mailing(request):
    if request.method == "POST":
        form = MailingForm(request.POST)
        if form.is_valid():
            try:
                mailing = form.cleaned_data["mailing"]
                successful = send_mailing(mailing.pk)
                messages.success(
                    request, f"Рассылка отправлена. Успешных отправок: {successful}"
                )
            except ValidationError as e:
                messages.error(request, str(e))
            return redirect("mailing_reports")
    else:
        form = MailingForm()
    return render(request, "messenger/send_mailing.html", {"form": form})


class MailingListView(generic.ListView):
    model = Mailing
    template_name = 'messenger/list_mailing.html'
    context_object_name = 'mailings'

    # @method_decorator(cache_page(60 * 5))
    # def dispatch(self, *args, **kwargs):
    #     return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()
        else:
            return Mailing.objects.filter(owner=self.request.user)

    def get_cache_key(self):
        return f"list_mailing_{self.request.user.id}"


class MailingCreateView(LoginRequiredMixin, generic.CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'messenger/mailing_form.html'
    success_url = reverse_lazy('messenger:list_mailing')
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'messenger/mailing_form.html'
    success_url = reverse_lazy('messenger:list_mailing')

    def get_object(self, queryset=None):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        if mailing.owner != self.request.user and not is_manager(self.request.user):
            raise PermissionDenied("Вы не можете редактировать эту рассылку.")
        return mailing


class MailingDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Mailing
    template_name = 'messenger/mailing_confirm_delete.html'
    success_url = reverse_lazy('messenger:list_mailing')

    def get_object(self, queryset=None):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        if mailing.owner != self.request.user and not is_manager(self.request.user):
            raise PermissionDenied("Вы не можете удалять эту рассылку.")
        return mailing


class HomeView(generic.TemplateView):
    template_name = 'messenger/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if is_manager(self.request.user):
                context['all_mailings'] = Mailing.objects.count()
                context['active_mailings'] = Mailing.objects.filter(status='Запущена').count()
                context['unique_recipients'] = Recipient.objects.count()
            else:
                context['all_mailings'] = Mailing.objects.filter(owner=self.request.user).count()
                context['active_mailings'] = Mailing.objects.filter(owner=self.request.user, is_active=True).count()
                context['unique_recipients'] = Recipient.objects.filter(owner=self.request.user).values('email').distinct().count()

        else:
            context['all_mailings'] = 0
            context['active_mailings'] = 0
            context['unique_recipients'] = 0
        return context


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'messenger/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self, queryset=None):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        if not is_manager(self.request.user) and mailing.owner != self.request.user:
            raise PermissionDenied("Вы не можете просматривать детали этой рассылки.")
        return mailing


class MailingDeactivateView(LoginRequiredMixin, View):
    context_object_name = 'messages'
    def get(self, request, pk):
        if not is_manager(request.user):
            raise PermissionDenied("Только менеджеры могут деактивировать рассылки.")

        mailing = get_object_or_404(Mailing, pk=pk)
        return render(request, 'messenger/mailing_deactivate_mailing.html', {'mailing': mailing})

    def post(self, request, pk):
        if not is_manager(request.user):
            raise PermissionDenied("Только менеджеры могут деактивировать рассылки")

        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_active = False
        mailing.save()
        messages.success(request, f"Рассылка '{mailing.name}' успешно деактивирована")
        return redirect('messenger:list_mailing')

@login_required
def mailing_reports(request):
    user = request.user
    mailing_logs = SendAttempt.objects.filter(mailing__owner=user).order_by("-date_time")
    context = {"mailing_logs": mailing_logs, "has_logs": mailing_logs.exists()}
    return render(request, "messenger/mailing_reports.html", context)


class MailingStatistView(LoginRequiredMixin, TemplateView):
    template_name = "messenger/mailing_statist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Общая статистика пользователя
        user_stats = SendAttempt.get_user_stats(user)

        # Статистика по каждой рассылке
        mailings = Mailing.objects.filter(owner=user)
        mailing_statist = []
        for mailing in mailings:
            stats = SendAttempt.get_mailing_stats(mailing)
            mailing_statist.append({
                "mailing": mailing,
                **stats
            })

        context.update({
            "user_stats": user_stats,
            "mailing_stats": mailing_statist,
        })
        return context
