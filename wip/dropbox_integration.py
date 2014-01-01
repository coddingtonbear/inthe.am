import hashlib
import json
import logging
import os


logger = logging.getLogger(__name__)


class DropboxSyncException(Exception):
    pass


class AbortDropboxSync(DropboxSyncException):
    pass


def find_tasks_in_dropbox(client):
    match_path = []
    matched_files = client.search('/', 'pending.data')
    for match in matched_files:
        if os.path.basename(match['path']) == 'pending.data':
            dir_name = os.path.dirname(match['path'])
            if dir_name not in match_path:
                match_path.append(dir_name)
    return match_path


def get_local_metadata(local_path):
    # Make sure the directory exists
    if not os.path.isdir(local_path):
        os.mkdir(local_path)

    # Check to see if we have stored metadata already
    if os.path.isfile(os.path.join(local_path, '.meta')):
        with open(os.path.join(local_path, '.meta')) as meta_file:
            meta = json.loads(meta_file.read())
    else:
        meta = {
            'files': {
            }
        }

    return meta


def set_local_metadata(local_path, metadata):
    with open(os.path.join(local_path, '.meta'), 'w') as meta_file:
        meta_file.write(json.dumps(metadata))


def get_files_newer_in_dropbox(client, dropbox_path, metadata):
    needs_update = []
    task_files = [
        'pending.data',
        'undo.data',
        'backlog.data',
        'completed.data',
    ]
    for filename in task_files:
        file_metadata = client.metadata(
            os.path.join(dropbox_path, filename)
        )
        local_version = metadata['files'].get(filename, {}).get('revision', -1)
        remote_version = file_metadata['revision']

        if local_version != remote_version:
            logger.info(
                "%s has changed in DropBox"
            )
            needs_update.append(local_version)

    return needs_update


def upload_changes_to_dropbox(client, dropbox_path, local_path):
    metadata = get_local_metadata(local_path)

    for filename, file_meta in metadata['files'].items():
        local_path = os.path.join(local_path, filename)
        remote_path = os.path.join(dropbox_path, filename)

        with open(local_path, 'r') as input_file:
            local_hash = hashlib.md5(input_file.read()).hexdigest()
            if local_hash != metadata['files']['md5']:
                logger.info(
                    '%s has changed locally'
                )
                input_file.seek(0)
                new_meta = client.put_file(
                    remote_path,
                    input_file,
                    overwrite=True,
                )
                new_meta['md5'] = local_hash
                metadata['files'][filename] = new_meta

    set_local_metadata(local_path, metadata)


def download_chanages_from_dropbox(client, dropbox_path, local_path):
    metadata = get_local_metadata(local_path)

    files_needing_update = get_files_newer_in_dropbox(
        client,
        dropbox_path,
        metadata,
    )

    for filename in files_needing_update:
        dropbox_file, file_meta = client.get_file_and_metadata(
            os.path.join(local_path, filename)
        )
        with dropbox_file:
            with open(os.path.join(local_path, filename), 'w') as out:
                contents = dropbox_file.read()
                out.write(contents)
                file_meta['md5'] = hashlib.md5(contents).hexdigest()
        metadata['files'][filename] = file_meta

    set_local_metadata(local_path, metadata)
