import email
import uuid

from behave import when
from django_mailbox.models import Mailbox


@when(u'the following incoming email is processed')
def handling_incoming_email(context):
    mailbox = Mailbox.objects.create(
        name='Temporary Mailbox'
    )
    # Temporary -- I need to figure out what these look like.
    with open('/tmp/%s' % uuid.uuid4(), 'w') as out:
        out.write(context.text)
    email_message = email.message_from_string(context.text)
    mailbox.process_incoming_message(email_message)
