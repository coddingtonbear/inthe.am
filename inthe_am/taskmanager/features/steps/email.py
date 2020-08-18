import email

from behave import when
from django_mailbox.models import Mailbox


@when(u"the following incoming email is processed")
def handling_incoming_email(context):
    mailbox = Mailbox.objects.create(name="Temporary Mailbox")
    email_message = email.message_from_string(context.text)
    mailbox.process_incoming_message(email_message)
