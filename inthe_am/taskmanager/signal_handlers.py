import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django_mailbox.signals import message_received
from rest_framework.authtoken.models import Token

from .models import TaskStore
from .tasks import process_email_message


logger = logging.getLogger(__name__)


def autoconfigure_taskd_if_necessary(instance):
    try:
        if not instance.configured:
            instance.autoconfigure_taskd()
    except:
        if not settings.DEBUG:
            raise
        message = "Error encountered while configuring task store."
        logger.exception(message)
        instance.log_error(message)


@receiver(
    models.signals.post_save,
    sender=User,
    dispatch_uid='generate_taskstore'
)
def create_taskstore_for_user(sender, instance, **kwargs):
    # This just makes sure that the task store exists.
    TaskStore.get_for_user(instance)
    Token.objects.get_or_create(user=instance)


@receiver(
    models.signals.post_save,
    sender=TaskStore,
    dispatch_uid='configure_taskstore'
)
def autoconfigure_taskstore_for_user(sender, instance, **kwargs):
    autoconfigure_taskd_if_necessary(instance)


@receiver(message_received, dispatch_uid='incoming_email')
def handle_incoming_message(sender, message, **kwargs):
    process_email_message.apply_async(args=(message.pk, ))
