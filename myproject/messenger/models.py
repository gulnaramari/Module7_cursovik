from django.db import models
from django.conf import settings
# Create your models here.


class Recipient(models.Model):
    email = models.EmailField(max_length=50, unique=True, help_text="Введите ваш е-майл")
    full_name = models.CharField(max_length=255, help_text="Введите ФИО")
    comment = models.TextField(verbose_name='Комментарии', blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE, related_name='recipients',
                              verbose_name='Владелец', null=True)

    class Meta:
        verbose_name = "получатель"
        verbose_name_plural = "получатели"
        ordering = ["email", "full_name"]
        permissions = [
            ('can_view_recipient', 'Can view recipient'),
        ]

    def __str__(self):
        return self.email




class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        ordering = ["subject"]


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('Created', 'Создана'),
        ('Started', 'Запущена'),
        ('Finished', 'Завершена')
        ]
    first_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Создана')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient)

    def __str__(self):
        return f"{self.status}"


class SendAttempt(models.Model):
    STATUS_CHOICES = [
        ('Done', 'Успешно'),
        ('Failed', 'Не успешно')
        ]

    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='send_attempts')

    def __str__(self):
        return f"Попытка рассылки: {self.attempt_time} - {self.status}"
