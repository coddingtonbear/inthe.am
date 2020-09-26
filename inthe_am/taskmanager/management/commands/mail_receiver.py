import email

from aiosmtpd.controller import Controller

from django.conf import settings
from django.core.management.base import BaseCommand

from django_mailbox.models import Mailbox


class IncomingMailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        if not address.endswith(f"@{settings.DOMAIN_NAME}"):
            return "550 not relaying to that domain"
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server, session, envelope):
        mbx, _ = Mailbox.objects.get_or_create(name=settings.INCOMING_TASK_MAILBOX_NAME)

        message = email.message_from_bytes(envelope.content)
        mbx.process_incoming_message(message)
        return "250 Message accepted for delivery"


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        controller = Controller(
            IncomingMailHandler(),
            hostname=settings.INCOMING_TASK_MAIL_HOSTNAME,
            port=settings.INCOMING_TASK_MAIL_PORT,
        )

        self.stdout.write(
            f"Listening for incoming mail on {controller.hostname}:{controller.port}"
        )

        try:
            controller.start()
            while True:
                continue
        except KeyboardInterrupt:
            controller.stop()
