from .settings import *


CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_REDIRECT_STDOUTS = True


# Redirect celery logging elsewhere.
for name, details in LOGGING["handlers"].items():
    if "filename" in details:
        if "celery" not in details["filename"]:
            details["filename"] = "".join(
                [
                    os.path.splitext(details["filename"])[0],
                    ".celery",
                    os.path.splitext(details["filename"])[1],
                ]
            )
