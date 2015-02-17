import os
import re


class TaskRc(object):
    def __init__(self, path, read_only=False):
        self.path = path
        self.read_only = read_only
        if not os.path.isfile(self.path):
            self.config, self.includes = {}, []
        else:
            self.config, self.includes = self._read(self.path)
        self.include_values = {}
        for include_path in self.includes:
            self.include_values[include_path], _ = self._read(
                os.path.abspath(include_path),
                include_from=self.path
            )

    def _read(self, path, include_from=None):
        config = {}
        includes = []
        if include_from and include_from.find(os.path.dirname(path)) != 0:
            return config, includes
        with open(path, 'r') as config_file:
            for line in config_file.readlines():
                line = line.decode('utf8', 'replace')
                if line.startswith('#'):
                    continue
                if line.startswith('include '):
                    try:
                        left, right = line.split(' ')
                        if right.strip() not in includes:
                            includes.append(right.strip())
                    except ValueError:
                        pass
                else:
                    try:
                        left, right = line.split('=')
                        key = left.strip()
                        value = right.strip()
                        config[key] = value
                    except ValueError:
                        pass
        return config, includes

    def _write(self, path=None, data=None, includes=None):
        if path is None:
            path = self.path
        if data is None:
            data = self.config
        if includes is None:
            includes = self.includes
        if self.read_only:
            raise AttributeError(
                "This instance is read-only."
            )
        with open(path, 'w') as config:
            for include in includes:
                config.write(
                    "include %s\n" % (
                        include
                    )
                )
            for key, value in data.items():
                config.write(
                    "%s=%s\n" % (
                        key.encode('utf8'),
                        value.encode('utf8')
                    )
                )

    @property
    def assembled(self):
        all_items = {}
        for include_values in self.include_values.values():
            all_items.update(include_values)
        all_items.update(self.config)
        return all_items

    def items(self):
        return self.assembled.items()

    def keys(self):
        return self.assembled.keys()

    def get(self, item, default=None):
        try:
            return self.assembled[item]
        except KeyError:
            return default

    def __getitem__(self, item):
        return self.assembled[item]

    def __setitem__(self, item, value):
        self.config[item] = str(value)
        self._write()

    def update(self, value):
        self.config.update(value)
        self._write()

    def get_udas(self):
        udas = {}

        uda_type = re.compile('^uda\.([^.]+)\.(type)$')
        uda_label = re.compile('^uda\.([^.]+)\.(label)$')
        for k, v in self.items():
            for matcher in (uda_type, uda_label):
                matches = matcher.match(k)
                if matches:
                    if matches.group(1) not in udas:
                        udas[matches.group(1)] = {}
                    udas[matches.group(1)][matches.group(2)] = v

        return udas

    def add_include(self, item):
        if item not in self.includes:
            self.includes.append(item)
        self._write()

    def __unicode__(self):
        return u'.taskrc at %s' % self.path

    def __str__(self):
        return self.__unicode__().encode('utf-8', 'REPLACE')
