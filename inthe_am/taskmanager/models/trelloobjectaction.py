from dateutil.parser import parse
from jsonfield import JSONField
import pytz

from django.db import IntegrityError, models

from ..context_managers import git_checkpoint
from .trelloobject import TrelloObject


class TrelloObjectAction(models.Model):
    type = models.CharField(max_length=100)
    action_id = models.CharField(max_length=100)
    model = models.ForeignKey(
        TrelloObject,
        related_name='actions',
        blank=True,
        null=True
    )
    meta = JSONField()

    occurred = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_from_request(cls, data):
        try:
            instance = cls.objects.create(
                action_id=data['action']['id'],
                type=data['action']['type'],
                model=TrelloObject.objects.get(pk=data['model']['id']),
                occurred=parse(
                    data['action']['date']
                ).replace(tzinfo=pytz.UTC),
                meta=data,
            )
        except IntegrityError:
            instance = cls.objects.get(
                action_id=data['action']['id'],
                model=TrelloObject.objects.get(pk=data['model']['id']),
            )

        model = instance.model
        model.meta = data['model']
        model.save()

        instance.reconcile_action()

        return instance

    def reconcile_createCard(self):
        # Run only for board events!
        if not self.model.type == TrelloObject.BOARD:
            return

        new_card_id = self.meta['action']['data']['card']['id']

        try:
            to = TrelloObject.objects.get(
                id=new_card_id,
                store=self.model.store,
            )
        except TrelloObject.DoesNotExist:
            to = TrelloObject.objects.create(
                id=new_card_id,
                store=self.model.store,
                type=TrelloObject.CARD,
                meta=self.meta['action']['data']['card'],
            )
            to.subscribe()
            with git_checkpoint(
                self.model.store,
                'Creating local task from Trello'
            ):
                self.model.store.client.task_add(
                    description=to.meta['name'],
                    intheamtrelloid=new_card_id,
                    intheamtrelloboardid=self.model.store.trello_board.pk
                )

        to.update_data()
        to.save()
        to.reconcile()

    def reconcile_action(self):
        self.model.reconcile()

        reconciliation_method = 'reconcile_%s' % self.type
        if hasattr(self, reconciliation_method):
            getattr(self, reconciliation_method)()

    def __unicode__(self):
        return (
            u'{type} action #{id} on trello {model_type} '
            '#{model_id}'.format(
                type=self.type.title(),
                id=self.id,
                model_type=self.model.type.title(),
                model_id=self.model.id
            )
        )

    class Meta:
        app_label = 'taskmanager'
