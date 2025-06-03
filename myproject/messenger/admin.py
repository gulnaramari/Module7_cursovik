from django.contrib import admin
from .models import Recipient, Message, Mailing, SendAttempt
# Register your models here.


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name")
    list_filter = ("full_name",)


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

