from rest_framework import serializers


class TaskSerializer(serializers.Serializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    short_id = serializers.IntegerField(source='id', read_only=True)
    status = serializers.CharField(required=False)
    urgency = serializers.FloatField(read_only=True)
    description = serializers.CharField(required=True)
    priority = serializers.CharField(required=False)
    project = serializers.CharField(required=False)
    due = serializers.DateTimeField(required=False)
    entry = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    start = serializers.DateTimeField(required=False)
    wait = serializers.DateTimeField(required=False)
    scheduled = serializers.DateTimeField(required=False)
    depends = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
    )
    blocks = serializers.SerializerMethodField()
    annotations = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    imask = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        self._store = kwargs.pop('store')
        super(TaskSerializer, self).__init__(*args, **kwargs)

    @property
    def store(self):
        return self._store

    def get_blocks(self, obj):
        blocks = self.store.client.filter_tasks({
            'depends.contains': obj['uuid'],
            'or': [
                ('status', 'pending'),
                ('status', 'waiting'),
            ]
        })
        return [b['uuid'] for b in blocks]

    def update(self, store, pk, data):
        for k, v in data.items():
            if not v:
                data.pop(k, None)

        original = store.client.get_task(uuid=pk)[1]
        for k, v in data.items():
            original[k] = v

        changes = original.get_changes(keep=True)
        store.client.task_update(original)

        return original, changes

    def create(self, store, data):
        for k, v in data.items():
            if not v:
                data.pop(k, None)

        return store.client.task_add(**data)
