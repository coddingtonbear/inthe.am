from dateutil.parser import parse
from jsonfield import JSONField
import pytz

from django.db import IntegrityError, models

from .trelloobject import TrelloObject


class TrelloObjectAction(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    type = models.CharField(max_length=100)
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
            return cls.objects.create(
                id=data['action']['id'],
                type=data['action']['type'],
                model=TrelloObject.objects.get(pk=data['model']['id']),
                occurred=parse(
                    data['action']['date']
                ).replace(tzinfo=pytz.UTC),
                meta=data,
            )
        except IntegrityError:
            return cls.objects.get(
                id=data['action']['id'],
            )

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
