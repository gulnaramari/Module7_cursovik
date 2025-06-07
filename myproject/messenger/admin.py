from django.contrib import admin
from .models import Recipient, Message, Mailing, SendAttempt
# Register your models here.


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'comment', 'owner')
    search_fields = ('email', 'full_name')
    list_filter = ('owner',)
    ordering = ('full_name',)
    readonly_fields = ('owner',)
    help_texts = {
        'comment': 'Введите дополнительную информацию о получателе'
    }

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "body")


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "first_at", "end_at", "status", "message_id")
    list_filter = ("status", "message_id")
    search_fields = ("end_at", "status", )


@admin.register(SendAttempt)
class SendAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "attempt_time", "status", "server_response", "mailing_id")
    list_filter = ("status", "mailing_id",)

