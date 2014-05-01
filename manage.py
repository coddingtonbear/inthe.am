#!/usr/bin/env python
import os

if os.environ.get('EVENTLET'):
    from eventlet.patcher import monkey_patch
    monkey_patch()

import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inthe_am.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
