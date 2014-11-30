from .settings import *


# Redirect celery logging elsewhere.
for name, details in LOGGING['handlers'].items():
    if 'filename' in details:
        details['filename'] = "".join([
            os.path.splitext(details['filename'])[0],
            '.celery',
            os.path.splitext(details['filename'])[1]
        ])

ANOTHER_SETTING = 'alpha'

with open('/tmp/wtf2.log', 'w') as output:
    import json
    output.write(
        json.dumps(LOGGING),
        indent=4,
    )
