import json
import os


class Metadata:
    def __init__(self, store, path):
        self.path = path
        self.store = store

        self.config = self._read()

    def _init(self):
        self.config = {
            "files": {},
            "taskrc": os.path.join(self.store.local_path, ".taskrc",),
        }
        self._write()
        return self.config

    def _read(self):
        if not os.path.isfile(self.path):
            return self._init()

        with open(self.path, "r") as config_file:
            return json.loads(config_file.read())

    def _write(self):
        with open(self.path, "w") as config_file:
            config_file.write(json.dumps(self.config))

    def items(self):
        return self.config.items()

    def keys(self):
        return self.config.keys()

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, item, value):
        self.config[item] = value
        self._write()

    def __str__(self):
        return f"metadata at {self.path}"
