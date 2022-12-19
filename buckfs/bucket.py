#!/usr/bin/env python3
# from abc import ABC, abstractmethod, abstractproperty
import pandas as pd
from typing import List
from typing import Dict
from .remote import Remote


class Bucket:
    """Encapsulate information about a bucket."""

    _tags_dir: str  # where are the tags kept
    _name: str  # the unique name of the bucket
    _Remotes: Dict[str, Remote]  # the remotes asociated with this bucket
    _roots: List[str]  # root directories of bucket on the local file system
    _cache: str  # path to the bucket sql like cache

    def __init__(self, roots: str, name: str, remotes: Remote):
        """Intitialise a bucket object that contains path."""
        assert type(roots) is list
        assert type(remotes) is dict
        assert type(name) is str
        self._roots = roots
        self._remotes = remotes
        self._name = name

    def get_files(self) -> pd.DataFrame:
        """Return a dataframe of files in the bucket."""
        pass

    def get_name(self) -> str:
        """Return unique bucket name."""
        return self._name

    @property
    def name(self) -> str:
        """Return name of bucket."""
        return self.get_name()

    def get_remotes(self) -> Dict[str, Remote]:
        """Return the remotes that are asociated with this bucket."""
        return self._Remotes

    def get_roots(self) -> List[str]:
        """Return the root paths to all bucket files on the local system."""
        return self._roots

    @property
    def roots(self) -> List[str]:
        """Return the root paths to all bucket files on the local system."""
        return self.get_roots()
