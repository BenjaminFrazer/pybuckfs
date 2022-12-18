"""Represents a single tracked object across all file systems."""

from remoteObject import RemoteObject
from localObject import LocalObject
from bucket import Bucket
from remote import Remote
from bfs import BFS
from typing import Dict


class SyncJob():
    """Represents a tracked object across all file systems."""

    _remote_instances: Dict[str, RemoteObject]  # instances of object in the remote
    _local_instance: LocalObject  # local instance of the object
    _bucket: Bucket  # the bucket to which these objects belong
    _remotes: Dict[str, Remote]
    _bfs: BFS  # the buckfs object

    def __init__(self, path: str):
        """Initialise Sync job class."""
        self._bfs = BFS()
        self._bucket = self._bfs.get_bucket_from_path(path)
        self._remotes = self._bucket.get_remotes()
        self._local_instance = LocalObject(path, Bucket)
        for name, remote in self._remotes.items():
            # instantiate a remote instance
            self._remote_instances[name] = RemoteObject(
                remote,
                self._local_instance.uuid)
        pass
