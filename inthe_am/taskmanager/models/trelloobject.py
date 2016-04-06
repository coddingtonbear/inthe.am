import datetime
import json
import logging
import pytz
import re
import requests

from dateutil.parser import parse
from jsonfield import JSONField
import trello

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models

from ..exceptions import CheckpointNeeded
from ..trello_utils import LABEL_COLORS, subscribe_to_updates
from ..utils import OneWaySafeJSONEncoder
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
    log = JSONField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    last_action = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_client_for_type(cls, type_name, store):
        cls = getattr(trello, type_name.title() + 's')
        return cls(
            settings.TRELLO_API_KEY,
            store.trello_auth_token,
        )

    def client_request(self, method, url, data):
        client = self.client

        return requests.request(
            method,
            'https://trello.com' + url,
            params=dict(key=client._apikey, token=client._token),
            data=data,
        )

    def add_log_data(self, message=None, data=None):
        log_data = self.log

        if not log_data:
            log_data = {
                'changes': []
            }

        data = json.loads(
            json.dumps(data, cls=OneWaySafeJSONEncoder)
        )

        changes = log_data.get('changes', [])

        changes.append({
            'occurred': str(datetime.datetime.now()),
            'message': message,
            'data': data,
        })

        log_data['changes'] = changes
        self.log = log_data
        self.save()

    def reconcile(self):
        self.add_log_data("Reconciliation initiated.")
        if not self.store.has_active_checkpoint():
            raise CheckpointNeeded()

        if self.type == self.CARD:
            return self._reconcile_card()
        elif self.type == self.BOARD:
            return self._reconcile_board()
        self.add_log_data("Reconciliation completed.")

    def _reconcile_board(self):
        known_lists = {
            c.pk: c for c in self.children.all()
        }

        for list_data in self.client.get_list(self.id):
            try:
                obj = TrelloObject.objects.get(
                    id=list_data.get('id')
                )
                self.add_log_data("Updating list %s" % list_data.get('id'))
                obj.meta = list_data
                obj.save()
                known_lists.pop(obj.pk, None)
            except TrelloObject.DoesNotExist:
                obj = TrelloObject.objects.create(
                    id=list_data.get('id'),
                    store=self.store,
                    type=TrelloObject.LIST,
                    parent=self.store.trello_board,
                    meta=list_data
                )
                self.add_log_data("Created list %s" % list_data.get('id'))
                obj.subscribe()

        for deleted_list in known_lists.values():
            deleted_list.delete()

    def _reconcile_card(self):
        try:
            task = self.store.client.filter_tasks({
                'intheamtrelloid': self.id,
                'intheamtrelloboardid': self.store.trello_board.id,
            })[0]
        except IndexError:
            self.add_log_data(
                "Could not find matching task; aborting task reconciliation."
            )
            return

        # In case a recurring task was stored, clear that out
        if task['status'] == 'recurring':
            self.add_log_data(
                "Matching task is recurring; aborting task reconciliation.",
                data=task,
            )
            return

        task['description'] = self.meta['name']
        task['intheamtrellodescription'] = self.meta['desc']
        task['intheamtrellourl'] = self.meta['url']
        if self.meta['badges']['due']:
            task['due'] = parse(self.meta['badges']['due'])

        try:
            list_data = TrelloObject.objects.get(id=self.meta['idList'])
            task['intheamtrellolistname'] = list_data.meta['name']
            task['intheamtrellolistid'] = list_data.id
        except self.DoesNotExist:
            task['intheamtrellolistname'] = ''
            task['intheamtrellolistid'] = ''
            logger.warning(
                "Unable to find list id %s when updating "
                "card id %s",
                self.meta['idList'],
                self.id,
            )

        task_tags = set(task.get('tags', []))

        # Remove any color labels, we'll re-add them below if they still apply
        for label_color in LABEL_COLORS:
            if label_color in task_tags:
                task_tags.remove(label_color)

        # Now, let's re-add any relevant tags by color and name
        for label in self.meta.get('labels', []):
            if label.get('color'):
                task_tags.add(label.get('color'))
            if label.get('name'):
                task_tags.add(
                    re.sub(
                        ur'[\W_]+', u'_',
                        label.get('name'),
                        flags=re.UNICODE
                    )
                )

        task['tags'] = sorted(list(task_tags))

        self.store.client.task_update(task)
        self.add_log_data("Task updated.", data=task)

        if self.meta['closed']:
            try:
                self.store.client.task_done(uuid=task['uuid'])
            except ValueError:
                # This just means the card was already closed.
                pass

    def update_trello(self, task):
        kwargs = {
            'name': task['description'],
        }
        if task.get('intheamtrellodescription'):
            kwargs['desc'] = task['intheamtrellodescription']
        if task['status'] in ('waiting', 'completed', 'deleted', ):
            return self.delete()

        # Set list if differs from current list
        list_id = task.get('intheamtrellolistid')
        if list_id and list_id != self.meta.get('idList'):
            kwargs['idList'] = list_id

        if task.get('due'):
            kwargs['due'] = pytz.UTC.normalize(task['due']).strftime(
                # 2016-01-31T20:00:00.000Z
                '%Y-%m-%dT%H:%M:%S.000Z'
            )

        logger.info(
            "Sending Trello update for task %s; Data: %s",
            task['uuid'],
            str(kwargs)
        )
        self.add_log_data(
            "Sending trello update data",
            data=kwargs
        )

        self.client.update(
            self.id,
            **kwargs
        )

        try:
            reformatter = re.compile(r'\W+')
            try:
                label_names = self.store.trello_board.meta.get(
                    'labelNames', {}
                )
            except (TypeError, AttributeError, ValueError):
                logger.exception("Error encountered while building label map.")
                label_names = {}
            # Maps string tag names to color names so we can know what
            # tags to add for whatever names.
            color_map = {
                reformatter.sub('_', v): k
                for (k, v) in label_names.items() if k
            }

            possible_colors = set(LABEL_COLORS)
            existing_labels = set([
                l.get('color')
                for l in self.meta.get('labels', [])
                if l.get('color')
            ])
            task_tags = set(task.get('tags'))
            for tag in task.get('tags'):
                if tag in color_map:
                    task_tags.add(color_map[tag])

            tags_to_add = (
                (task_tags - existing_labels) & possible_colors
            )
            for tag_to_add in tags_to_add:
                self.client.new_label(self.id, tag_to_add)

            tags_to_delete = (
                (existing_labels - task_tags) & possible_colors
            )
            for tag_to_delete in tags_to_delete:
                self.client.delete_label_color(tag_to_delete, self.id)
        except:
            logger.exception("Error encountered while adding labels!")

    @classmethod
    def create(cls, **kwargs):
        store = kwargs.pop('store')
        type = kwargs.pop('type')
        parent = kwargs.pop('parent', None)

        client = cls.get_client_for_type(type, store)

        meta = client.new(**kwargs)

        instance = cls.objects.create(
            id=meta['id'],
            store=store,
            parent=parent,
            type=type,
            meta=meta,
        )
        instance.add_log_data(
            "Instance created",
            data={
                'meta': meta,
                'head': store.repository.head(),
            }
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
                        'secret_id': self.store.secret_id,
                    }
                )
            )
            self.add_log_data("Subscribing to updates.")
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

    def update_data(self):
        self.meta = self.get_data()

    def delete(self, *args, **kwargs):
        try:
            self.add_log_data("Deleting record.")
            if not self.deleted:
                self.client.update_closed(self.id, 'true')
                self.deleted = True
                self.save()
        except Exception as e:
            logger.exception(
                'Error encountered while deleting remote Trello object: %s',
                str(e)
            )

    def __unicode__(self):
        return u'Trello {type} #{id} ({user})'.format(
            type=self.type.title(),
            id=self.id,
            user=self.store.user.username,
        )

    class Meta:
        app_label = 'taskmanager'
