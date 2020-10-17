import logging
import os
import time

from django.apps import AppConfig
from django.conf import settings

from .taskd import TaskdAccountManager, TaskdAccountManagementError


logger = logging.getLogger(__name__)


class TaskmanagerConfig(AppConfig):
    name = "inthe_am.taskmanager"
    verbose_name = "Task Manager"

    def ready(self):
        cert_path = settings.CA_CERT_PATH

        super().ready()

        for _ in range(30):
            if not os.path.exists(cert_path):
                try:
                    ca_cert = TaskdAccountManager.get_ca_cert()
                except TaskdAccountManagementError:
                    time.sleep(1)
                    continue
                with open(cert_path, "w") as outf:
                    outf.write(ca_cert)
                    logger.info(f"Wrote current certificate to {cert_path}.")
