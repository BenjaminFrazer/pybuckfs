"""Represents a single tracked object across all file systems."""

from .remoteObject import RemoteObject
from .localObject import LocalObject
from .bucket import Bucket
from .remote import Remote
from .bfs import BFS
from typing import Dict, List


class SyncJob():
    """Represents a tracked object across all file systems."""

    _remote_instances: Dict[str, RemoteObject]  # instances of object in the remote
    _local_instances: List[LocalObject]  # local instance of the object
    _bucket: Bucket  # the bucket to which these objects belong
    _remotes: Dict[str, Remote]
    _uuid: str
    _bfs: BFS  # the buckfs object

    def __init__(self, path: str, bucket: Bucket, sync_all_locals: bool=False):
        """Initialise Sync job class."""
        self._bfs = BFS()
        self._bucket = bucket
        self._remotes = self._bucket.get_remotes()
        self._local_instances = [LocalObject(str)]
        self._uuid = self._local_instances[0].uuid
        if sync_all_locals:
            self._local_instances.extend(self._bfs.get_local_instances(UUID))
        for name, remote in self._remotes.items():
            # instantiate a remote instance
            self._remote_instances[name] = RemoteObject(
                remote,
                self._local_instance.uuid)

    def sync(self):
        """Begin synchronisation."""
        # decide which instance is the most recent
        pass
