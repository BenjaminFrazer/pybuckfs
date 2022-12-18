#/usr/bin/env python3
"""Class for working with invoked directories in buckfs."""
from buckfs import BFS
import re
import pandas as pd
from typing import Generator
from bucket import Bucket
# from abc import ABC, abstractmethod, abstractproperty
# from typing import List
# from typing import Dict
# import yaml
from pathlib import Path


class Dir:
    """Contains information about the invocation directory."""

    _bfs: BFS
    _invocation_dir: str  # Where was this command invoked
    _file_list: pd.DataFrame  # A list of all the tracked files in this directory
    # generator for all tracked files yeilding a Path object
    _file_gen: Generator[Path]
    _bucket: Bucket

    def __init__(self, dir: str, *args, **kwargs):
        """Initialise dir."""
        self._invocation_dir = dir
        # build a list of all tracked files in the directory
        self._get_tracked_files()

    def sync(self):
        """Synchronise the directory content with all remotes."""
        pass

    def _get_bucket_root(self):
        """Find out where the bucket root is."""
        pass

    def _get_cache(self):
        pass

    def _get_tracked_files(self) -> Generator[Path]:
        """Return all tracked files."""
        # create a generator of all files
        file_gen = self._get_all_files()
        for this_file in file_gen:

    def _handle_file(self, Path):
        # first check if the file is in the cache
        pass


    def _get_all_files(self) -> Generator[Path]:
        """Return all files in the invoked directory."""
        pass


# for testing
if __name__ =="main":
        example_file_names=[
            "/tmp/my files/my haiku [shesk].txt\n\
            /usr/my haiku [ush4wjHseK]"
            ]
