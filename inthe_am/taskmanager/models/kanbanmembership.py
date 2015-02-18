import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string


class KanbanMembershipManager(models.Manager):
    def active(self):
        return super(KanbanMembershipManager, self).get_queryset().filter(
            valid=True,
            accepted=True,
        )

    def pending(self):
        return super(KanbanMembershipManager, self).get_queryset().filter(
            valid=True,
            accepted=False,
        )

    def owners_of(self, kanban_board):
        return self.active().filter(
            role=KanbanMembership.OWNER,
            kanban_board=kanban_board,
        )

    def members_of(self, kanban_board):
        return self.active().filter(
            kanban_board=kanban_board
        )

    def user_is_member(self, kanban_board, user):
        return self.members_of(kanban_board).filter(
            member=user
        ).exists()

    def user_is_owner(self, kanban_board, user):
        return self.owners_of(kanban_board).filter(
            member=user
        ).exists()


class KanbanMembership(models.Model):
    OWNER = 'owner'
    MEMBER = 'member'

    ROLES = (
        (OWNER, 'Owner', ),
        (MEMBER, 'Member', ),
    )

    uuid = models.CharField(
        max_length=36,
        db_index=True,
        blank=True,
    )
    kanban_board = models.ForeignKey(
        'KanbanBoard',
        related_name='memberships',
        db_index=True,
    )
    sender = models.ForeignKey(
        User,
        related_name='sent_memberships',
    )
    member = models.ForeignKey(
        User,
        related_name='kanban_memberships',
        null=True,
        blank=True,
        db_index=True,
    )
    invitee_email = models.EmailField(
        max_length=254,
        db_index=True,
        blank=True,
    )
    role = models.CharField(
        max_length=255,
        choices=ROLES,
        default=MEMBER
    )
    accepted = models.BooleanField(default=False)
    valid = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    objects = KanbanMembershipManager()

    def reject(self):
        self.valid = False
        self.accepted = False

    def accept(self):
        self.valid = True
        self.accepted = True

    @property
    def invitee(self):
        User.objects.get(email=self.invitee_email)

    @classmethod
    def invite_user(cls, board, sender, email, role, send_email=True):
        invitation = cls.objects.create(
            kanban_board=board,
            sender=sender,
            invitee_email=email,
            role=role,
        )
        invitation.send_email()

    def send_email(self):
        ctx = {
            'sender': self.sender,
            'kanban_board': self.kanban_board,
            'uuid': self.uuid,
        }
        text_content = render_to_string('kanban_invitation.txt', ctx)
        html_content = render_to_string('kanban_invitation.html', ctx)
        msg = EmailMultiAlternatives(
            '%s would like you to join the %s Kanban Board' % (
                self.sender.first_name
                if self.sender.first_name
                else 'Somebody',
                self.kanban_board.name,
            ),
            text_content,
            settings.SERVER_EMAIL,
            [self.invitee_email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send(fail_silently=False)

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        super(KanbanMembership, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.valid and self.accepted:
            return "%s level membership to %s by %s" % (
                self.role,
                self.kanban_board,
                self.member,
            )
        elif self.valid and not self.accepted:
            return "(Pending Invitation) %s level membership to %s by %s" % (
                self.role,
                self.kanban_board,
                self.member,
            )
        elif not self.valid:
            return "(Rejected Invitation) %s level membership to %s by %s" % (
                self.role,
                self.kanban_board,
                self.member,
            )

    class Meta:
        app_label = 'taskmanager'
