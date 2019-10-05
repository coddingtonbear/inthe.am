from rest_framework import serializers


class TaskSerializer(serializers.Serializer):
    id = serializers.UUIDField(source='uuid', read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    short_id = serializers.IntegerField(source='id', read_only=True)
    status = serializers.CharField(required=False)
    urgency = serializers.FloatField(read_only=True)
    description = serializers.CharField(required=True)
    priority = serializers.CharField(required=False, allow_blank=True)
    project = serializers.CharField(required=False, allow_blank=True)
    due = serializers.DateTimeField(required=False)
    entry = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)
    start = serializers.DateTimeField(required=False)
    wait = serializers.DateTimeField(required=False)
    until = serializers.DateTimeField(required=False)
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
    udas = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self._store = kwargs.pop('store')
        super(TaskSerializer, self).__init__(*args, **kwargs)

    @property
    def store(self):
        return self._store

    def get_udas(self, obj):
        udas = {}
        for field in self.store.client.config.get_udas().keys():
            if field in obj:
                udas[field] = obj[field]

        return udas

    def get_blocks(self, obj):
        return self.store.get_blocks_for_task(obj)

    def update(self, store, pk, data):
        original = store.client.get_task(uuid=pk)[1]
        for k, v in data.items():
            if k == 'priority' and v == '':
                v = None
            original[k] = v

        changes = original.get_changes(keep=True)
        store.client.task_update(original)

        return original, changes

    def create(self, store, data):
        record = {}

        for k, v in data.items():
            if v:
                record[k] = v

        return store.client.task_add(**record)
