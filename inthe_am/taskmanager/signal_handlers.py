import logging
import mimetypes
import traceback

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.db import models
from django.dispatch import receiver
from django_mailbox.signals import message_received
from rest_framework.authtoken.models import Token

from .models import TaskStore
from .tasks import process_email_message


logger = logging.getLogger(__name__)


@receiver(models.signals.post_save, sender=User, dispatch_uid="generate_taskstore")
def create_taskstore_for_user(sender, instance, **kwargs):
    # This just makes sure that the task store exists.
    store = TaskStore.get_for_user(instance)
    Token.objects.get_or_create(user=instance)
    if not store.configured:
        store.autoconfigure_taskd()
        store.taskd_account.suspend()


@receiver(message_received, dispatch_uid="incoming_email")
def handle_incoming_message(sender, message, **kwargs):
    process_email_message.apply_async(args=(message.pk,))


@receiver(message_received, dispatch_uid="forwardable_email")
def handle_incoming_forwardable_message(sender, message, **kwargs):
    for address in message.to_addresses:
        if address in settings.MAIL_FORWARDING:
            try:
                email = EmailMultiAlternatives(
                    subject=" ".join(
                        ["[Inthe.AM]", message.subject, f"({message.pk})"]
                    ),
                    body=message.text,
                    to=[settings.MAIL_FORWARDING[address]],
                    reply_to=[message.from_header],
                    headers={"IntheAM-Message-Id": message.pk},
                )
                email.attach_alternative(
                    message.html,
                    "text/html",
                )
                for attachment in message.attachments.all():
                    email.attach(
                        attachment.get_filename(),
                        attachment.document.read(),
                        mimetypes.guess_type(
                            attachment.get_filename(),
                        )[0],
                    )
                email.send()
            except Exception:
                mail_admins(
                    f"Error processing forwarding rule for {address}",
                    f"See message ID {message.pk}.\n\n{traceback.format_exc()}",
                )
