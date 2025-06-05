from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

from clients.models import Client
from mail_messages.models import Message
from mailings.models import Mailing


class Command(BaseCommand):
    help = 'Создание группы Менеджеры и назначение прав'

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name='Менеджеры')

        permissions = [
            ('recipients', 'recipient', 'can_view_recipient'),
            ('mailings', 'mailing', 'can_view_mailing'),
            ('users', 'user', 'block_user'),
            ('mail_messages', 'message', 'can_view_message'),
        ]

        for app_label, model, codename in permissions:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            permission = Permission.objects.get(codename=codename, content_type=content_type)
            group.permissions.add(permission)

        group.save()
        self.stdout.write(self.style.SUCCESS("Группа 'Менеджеры' создана/обновлена с необходимыми правами."))