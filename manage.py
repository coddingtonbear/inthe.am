#!/usr/bin/env python
import os

if os.environ.get('EVENTLET'):
    from eventlet.patcher import monkey_patch
    monkey_patch()

import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inthe_am.settings")

    from django.core.management import execute_from_command_line
    from django.conf import settings

    if settings.DEBUG:
        if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
            import ptvsd
            ptvsd.enable_attach(address=('0.0.0.0', 3000))

    execute_from_command_line(sys.argv)
