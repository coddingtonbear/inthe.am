from jsonfield import JSONField
import logging
import trello

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from ..trello_utils import subscribe_to_updates
from .taskstore import TaskStore


logger = logging.getLogger(__name__)


class TrelloObject(models.Model):
    CARD = 'card'
    BOARD = 'board'
    LIST = 'list'

    TYPE_CHOIES = (
        (CARD, 'Card', ),
        (BOARD, 'Board', ),
        (LIST, 'List', )
    )

    DOING = 'Doing'
    TO_DO = 'To Do'
    WAITING = 'Waiting'
    CLOSED = 'Closed'
    DELETE = 'Delete'

    id = models.CharField(primary_key=True, max_length=100)
    store = models.ForeignKey(
        TaskStore,
        related_name='trello_objects',
    )
    parent = models.ForeignKey(
        'self',
        related_name='children',
        null=True,
        blank=True,
    )
    type = models.CharField(choices=TYPE_CHOIES, max_length=10)
    meta = JSONField()

    @classmethod
    def get_client_for_type(cls, type_name, store):
        cls = getattr(trello, type_name.title() + 's')
        return cls(
            settings.TRELLO_API_KEY,
            store.trello_auth_token,
        )

    @classmethod
    def create(cls, **kwargs):
        store = kwargs.pop('store')
        type = kwargs.pop('type')
        parent = kwargs.pop('parent', None)

        client = cls.get_client_for_type(type, store)

        meta = client.new(**kwargs)

        instance = cls.objects.create(
            id=meta.get('id'),
            store=store,
            parent=parent,
            type=type,
            meta=meta,
        )
        instance.subscribe()
        return instance

    @property
    def client(self):
        if not hasattr(self, '_client'):
            self._client = self.get_client_for_type(
                self.type,
                self.store,
            )

        return self._client

    def subscribe(self):
        try:
            subscribe_to_updates(
                self.id,
                self.store.trello_auth_token,
                reverse(
                    'trello_incoming',
                    kwargs={
                        'api_name': 'v1',
                        'resource_name': 'task',
                        'secret_id': self.store.secret_id,
                    }
                )
            )
        except RuntimeError as e:
            logger.exception(
                "Error encountered while subscribing to Trello updates: %s",
                str(e)
            )

    def update_using_method(self, method_name, *args, **kwargs):
        method = getattr(self.client, method_name)
        self.meta = method(*args, **kwargs)
        self.save()

    def get_list_by_type(self, name):
        if self.type != self.BOARD:
            raise ValueError("This method is valid only for Board objects.")

        for l in self.children.all():
            if l.meta['name'] == name:
                return l

        raise TrelloObject.DoesNotExist()

    def get_data(self):
        return self.client.get(self.id)

    def __unicode__(self):
        return u'Trello {type} #{id} ({user})'.format(
            type=self.type.title(),
            id=self.id,
            user=self.store.user.username,
        )

    def delete(self, *args, **kwargs):
        try:
            self.client.update_closed(self.id, 'true')
        except Exception as e:
            logger.exception(
                'Error encountered while deleting remote Trello object: %s',
                str(e)
            )
        super(TrelloObject, self).delete(*args, **kwargs)

    class Meta:
        app_label = 'taskmanager'
