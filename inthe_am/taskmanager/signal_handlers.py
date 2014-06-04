import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django_mailbox.signals import message_received
from tastypie.models import create_api_key

from .models import TaskStore
from .tasks import process_email_message


logger = logging.getLogger(__name__)


# Generate an API key automatically
models.signals.post_save.connect(
    create_api_key, sender=User, dispatch_uid='generate_api'
)


@receiver(models.signals.post_save, sender=User, dispatch_uid='generate_taskd')
def autoconfigure_taskd_for_user(sender, instance, **kwargs):
    store = TaskStore.get_for_user(instance)
    try:
        if not store.configured:
            store.autoconfigure_taskd()
    except:
        if not settings.DEBUG:
            raise
        message = "Error encountered while configuring task store."
        logger.exception(message)
        store.log_error(message)


@receiver(message_received, dispatch_uid='incoming_email')
def handle_incoming_message(sender, message, **kwargs):
    process_email_message.apply_async(args=(message.pk, ))
