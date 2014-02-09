import logging
import os
import sys


logger = logging.getLogger(__name__)


CURRENT_TASKSTORE_VERSION = 1


def upgrade(store):
    while store.version < CURRENT_TASKSTORE_VERSION:
        target_version = store.version + 1
        migrator = getattr(
            sys.modules[__name__],
            'migrate_%s' % target_version,
            None
        )
        if migrator is None:
            logger.error(
                'Attempted to migrate %s to %s but migration not found!',
                store,
                target_version,
            )
            return
        try:
            migrator(store)
            store.version = target_version
            logger.info(
                'Migration of %s to %s was completed successfully.',
                store,
                target_version,
            )
        except Exception:
            logger.exception(
                'Attempted to migrate %s to %s but exception occurred!',
                store,
                target_version
            )
            raise


def migrate_1(store):
    with open(os.path.join(store.local_path, '.gitignore'), 'w') as out:
        out.write('.lock\n')
