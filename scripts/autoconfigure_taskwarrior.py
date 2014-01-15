#!/usr/bin/env python
import datetime
import os.path
import shutil


def set_taskrc_properties(self, kvps):
    taskrc_path = os.path.expanduser('~/.taskrc') + '.%s.bak' % (
        datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    )
    backup_taskrc_path = os.path.expanduser('~/.taskrc') + '.%s.bak' % (
        datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    )
    shutil.copy(taskrc_path, backup_taskrc_path)
    print "Backup copy saved to %s" % backup_taskrc_path

    taskrc = open(os.path.expanduser('~/.taskrc'), 'r')
    lines = taskrc.readlines()
    taskrc.close()

    found_keys = []
    for idx, line in enumerate(lines):
        parts = [l.strip() for l in line.split('=')]
        if len(parts) < 1:
            continue
        for key, value in kvps.items():
            if parts[0] == key:
                line[idx] = "%s=%s" % (
                    key,
                    value
                )
                found_keys.append(key)

    for key, value in kvps.items():
        if key not in found_keys:
            lines.append(
                "%s=%s" % (
                    key,
                    value,
                )
            )

    taskrc = open(os.path.expanduser('~/.taskrc'), 'w')
    for line in lines:
        taskrc.write(line + '\n')
    taskrc.close()


def get_file():
    pass


def main(self):
    pass

