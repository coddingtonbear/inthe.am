import os
import re
import subprocess
from typing import Dict, List, cast
from typing_extensions import Literal


class TaskRc:
    def __init__(self, path: str, read_only=False):
        self.path = path
        self.read_only = read_only
        if not os.path.isfile(self.path):
            self.config, self.includes = {}, []
        else:
            self.config, self.includes = self._read(self.path)
        self.include_values = {}
        for include_path in self.includes:
            self.include_values[include_path], _ = self._read(
                os.path.abspath(include_path), include_from=self.path
            )

    def _read(self, path: str, include_from: str = None):
        config: Dict[str, str] = {}
        includes: List[str] = []
        if include_from and include_from.find(os.path.dirname(path)) != 0:
            return config, includes
        with open(path, "r") as config_file:
            for line in config_file.readlines():
                if line.startswith("#"):
                    continue
                if line.startswith("include "):
                    try:
                        left, right = line.split(" ")
                        if right.strip() not in includes:
                            includes.append(right.strip())
                    except ValueError:
                        pass
                else:
                    try:
                        left, right = line.split("=")
                        key = left.strip()
                        value = right.strip()
                        config[key] = value
                    except ValueError:
                        pass
        return config, includes

    def _write(
        self, path: str = None, data: Dict[str, str] = None, includes: List[str] = None
    ):
        if path is None:
            path = self.path
        if data is None:
            data = self.config
        if includes is None:
            includes = self.includes
        if self.read_only:
            raise AttributeError("This instance is read-only.")
        with open(path, "w") as config:
            for include in includes:
                config.write(f"include {include}\n")
            for key, value in data.items():
                config.write(f"{key}={value}\n")

    @property
    def assembled(self) -> Dict[str, str]:
        all_items = {}
        for include_values in self.include_values.values():
            all_items.update(include_values)
        all_items.update(self.config)
        return all_items

    def items(self):
        return self.assembled.items()

    def keys(self):
        return self.assembled.keys()

    def get(self, item: str, default=None):
        try:
            return self.assembled[item]
        except KeyError:
            return default

    def __getitem__(self, item: str):
        return self.assembled[item]

    def __setitem__(self, item: str, value: str):
        self.config[item] = str(value)
        self._write()

    def update(self, value: Dict[str, str]):
        self.config.update(value)
        self._write()

    def get_udas(self) -> Dict[str, Dict[Literal["type", "label"], str]]:
        udas: Dict[str, Dict[Literal["type", "label"], str]] = {}

        uda_type = re.compile(r"^uda\.([^.]+)\.(type)$")
        uda_label = re.compile(r"^uda\.([^.]+)\.(label)$")
        for k, v in self.items():
            for matcher in (uda_type, uda_label):
                matches = matcher.match(k)
                if matches:
                    if matches.group(1) not in udas:
                        udas[matches.group(1)] = {}
                    udas[matches.group(1)][
                        cast(Literal["type", "label"], matches.group(2))
                    ] = v

        return udas

    def add_include(self, item) -> None:
        if item not in self.includes:
            self.includes.append(item)
        self._write()

    def remove_include(self, item) -> None:
        if item in self.includes:
            self.includes.remove(item)
        self._write()

    def get_certificate_fingerprint(self) -> str:
        fp_proc = subprocess.Popen(
            [
                "certtool",
                "--hash",
                "SHA512",
                "--fingerprint",
                "--infile",
                self["taskd.certificate"],
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return fp_proc.communicate()[0].decode("utf-8").strip()

    def __str__(self):
        return f".taskrc at {self.path}"
