from django.db import models
from django.conf import settings
from django.utils import timezone
from users.models import User


class Recipient(models.Model):
    email = models.EmailField(max_length=50, unique=True, help_text="Введите ваш е-майл")
    full_name = models.CharField(max_length=255, help_text="Введите ФИО")
    comment = models.TextField(verbose_name='Комментарии', blank=True, null=True)
    owner = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              verbose_name='Владелец',
                              help_text="Укажите владельца",
                              null=True,
                              blank=True, )

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
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец',
        null=True
    )

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        ordering = ["subject"]
        permissions = [
            ('can_view_message', 'Can view message'),
        ]


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('Created', 'Создана'),
        ('Started', 'Запущена'),
        ('Finished', 'Завершена')
    ]
    first_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Создана')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение', related_name='mailings')
    recipients = models.ManyToManyField(Recipient, verbose_name='Получатели', related_name='mailings')
    start_date_time = models.DateTimeField(verbose_name='Дата и время первой отправки', blank=True, null=True,
                                           editable=False)
    end_date_time = models.DateTimeField(verbose_name='Дата и время окончания отправки', blank=True, null=True,
                                         editable=False)

    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              verbose_name='Владелец', null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        permissions = [
            ("can_view_all_mailings", "Может просматривать все рассылки"),
            ("can_disable_mailings", "Может отключать рассылки"),
        ]

    def __str__(self):
        return f'Рассылка: {self.message} | Статус: {self.get_status_display()}'


class SendAttempt(models.Model):
    STATUS_CHOICES = [
        ('Done', 'Успешно'),
        ('Failed', 'Не успешно')
    ]

    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='Failed', verbose_name='Статус',
                              db_index=True
                              )
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE,
                                verbose_name='Рассылка', null=True, related_name='sendattempt')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE,
                                  verbose_name='Получатель', null=True, related_name='sendattempt')
    date_time = models.DateTimeField(default=timezone.now,
                                     verbose_name='Дата и время попытки', db_index=True,
                                     editable=False)
    server_response = models.TextField(verbose_name='Ответ почтового сервера', blank=True, null=True)

    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылки'
        ordering = ['-date_time']

    def __str__(self):
        return f"{self.mailing} - {self.recipient.email} - {self.date_time} - {self.status}"

    @classmethod
    def get_user_stats(cls, user):
        """Общая статистика по пользователю"""
        logs = cls.objects.filter(mailing__owner=user)
        total = logs.count()
        success = logs.filter(status="Done").count()
        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "success_rate": (success / total * 100) if total > 0 else 0,
        }
