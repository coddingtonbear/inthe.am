import email
import uuid

from behave import when
from django_mailbox.models import Mailbox, Message

from inthe_am.taskmanager.tasks import process_email_message


@when(
    u'an incoming task creation e-mail having the subject '
    u'"{subject}" and the following body is received'
)
def handling_incoming_email(context, subject):
    mailbox = Mailbox.objects.create(
        name='Temporary Mailbox'
    )
    message = Message.objects.create(
        mailbox=mailbox,
        subject=subject,
        body=str(
            email.message_from_string(context.text),
        ),
        message_id=str(uuid.uuid4()),
        to_header='@'.join([
            context.store.secret_id,
            'inthe.am'
        ]),
        from_header='anonymous@somewhere.com',
    )
    process_email_message(message.pk)
