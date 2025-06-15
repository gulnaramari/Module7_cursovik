from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils import timezone

from .models import Recipient, Mailing, SendAttempt

def is_manager(user):
    return user.groups.filter(name='Менеджеры').exists()


def validate_mailing_time(mailing):
    "Проверка времени у рассылки"
    now = timezone.now()

    if mailing.status == "Finished":
        raise ValidationError("Рассылка завершена и ее нельзя повторно запустить")

    if mailing.start_date_time and now < mailing.start_date_time:
        raise ValidationError("Рассылка еще не началась")

    if mailing.end_date_time and now > mailing.end_date_time:
        raise ValidationError("Рассылка уже завершена")

    if mailing.status != "Started":
        mailing.status = "Started"
        if not mailing.start_date_time:
            mailing.start_date_time = now
        mailing.save()


def send_mailing(mailing_id):
    """Отправка рассылки"""
    try:
        mailing = Mailing.objects.get(pk=mailing_id)
        validate_mailing_time(mailing)

        if not mailing.messenger.exists():
            raise ValidationError("Нет получателей для рассылки.")

        for recipient in mailing.messenger.all():
            try:
                send_single_email(mailing, recipient)
            except Exception as e:
                SendAttempt.objects.create(
                    mailing=mailing,
                    client=recipient,
                    status="Failed",
                    server_response=str(e),
                )

        if mailing.end_date_time and timezone.now() > mailing.end_date_time:
            mailing.status = "Finished"
            mailing.save()

    except Mailing.DoesNotExist:
        raise ValidationError(f"Рассылка с ID {mailing_id} не найдена.")
    except Exception as e:
        raise ValidationError(str(e))


def send_single_email(mailing, recipient):
    """Отправляет одно письмо конкретному клиенту."""
    if not recipient.email:
        raise ValueError("У клиента не указан email.")

    subject = mailing.message.message_subject
    message = mailing.message.message_body
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [recipient.email]

    send_mail(subject, message, from_email, recipient_list)
    SendAttempt.objects.create(
        mailing=mailing, client=recipient, status="Done", server_response="OK"
    )


def get_mailing_statistics(user=None):
    "Возвращает статистику рассылок для всех пользователей или для конкретного пользователя"

    if user and not is_manager(user):
        mailings = Mailing.objects.filter(owner=user)
    else:
        mailings = Mailing.objects.all()

    total_mailings = mailings.count()
    active_mailings_count = mailings.filter(is_active=True).count()
    unique_clients = Recipient.objects.filter(mailings__in=mailings).distinct().count()

    return {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings_count,
        "unique_clients": unique_clients,
    }
