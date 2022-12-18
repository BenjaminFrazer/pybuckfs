#!/usr/bin/env python3
"""Defines common behavoir for any tracked object/file in buckfs."""
import hashlib
from abc import ABC  # , abstractmethod, abstractproperty
# from typing import Dict
from pathlib import Path

import os


class LocalObject(ABC):
    """Common base class for any tracked buckfs object."""

    _filepath: Path  #
    _uuid: str
    # _remoteObjects: Dict[str, remoteObject]

    def __init__(self, path: str):
        """Initialise Tracked object."""
        _filepath: os.path.expanduser(path)

    def uuid(self) -> str:
        """Return the uuid of the object."""
        return self._uuid

    def _get_current_md5_checksum(self):
        m = hashlib.md5()
        with open(self._filepath, 'rb') as f:
            for data in iter(lambda: f.read(1024 * 1024), b''):
                m.update(data)
        return m.hexdigest()

    def _get_s3_double_checksum(self):
        chunk_size = 8 * 1024 * 1024
        md5s = []
        with open(self._filepath, 'rb') as f:
            for data in iter(lambda: f.read(chunk_size), b''):
                md5s.append(hashlib.md5(data).digest())
        m = hashlib.md5("".join(md5s))
        return '{}-{}'.format(m.hexdigest(), len(md5s))


if __name__ == "main":
    test_file = os.path.expanduser("~/data/test buckfs/test_file.txt")
    obj = LocalObject(test_file)
    print(obj._get_current_md5_checksum(test_file))
