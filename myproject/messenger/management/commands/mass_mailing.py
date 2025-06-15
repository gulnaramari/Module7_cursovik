from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from myproject.messenger.models import Recipient, Mailing, SendAttempt


class Command(BaseCommand):
    help = "Отправляет массовую рассылку по ID рассылки"

    def add_arguments(self, parser):
        parser.add_argument(
            "mailing_id", type=int, help="ID рассылки, которую нужно отправить"
        )

    def handle(self, *args, **options):
        mailing_id = options["mailing_id"]
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Рассылка с ID "{mailing_id}" не найдена.')

        if not mailing.is_active:
            self.stdout.write(
                self.style.WARNING(
                    f'Рассылка с ID "{mailing_id}" не активна. Отправка не будет произведена.'
                )
            )
            return

        recipients = Recipient.objects.all()

        for rec in recipients:
            try:
                send_mail(
                    mailing.title,
                    mailing.body,
                    settings.EMAIL_HOST_USER,
                    [rec.email],
                    fail_silently=False,
                )
                SendAttempt.objects.create(
                    mailing=mailing,
                    client=rec,
                    status="successfully",
                    date_time=timezone.now(),
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Успешно отправлено клиенту: {rec.email}")
                )

            except Exception as e:
                SendAttempt.objects.create(
                    mailing=mailing,
                    client=rec,
                    status="not_successful",
                    server_response=str(e),
                    date_time=timezone.now(),
                )
                self.stdout.write(
                    self.style.ERROR(f"Ошибка отправки клиенту {rec.email}: {e}")
                )

        self.stdout.write(self.style.SUCCESS("Рассылка успешно завершена."))
