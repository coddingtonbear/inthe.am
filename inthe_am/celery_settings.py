from .settings import *


# Redirect celery logging elsewhere.
for name, details in LOGGING['handlers'].items():
    if 'filename' in details:
        details['filename'] = "".join([
            os.path.splitext(details['filename'])[0],
            '.celery',
            os.path.splitext(details['filename'])[1]
        ])
