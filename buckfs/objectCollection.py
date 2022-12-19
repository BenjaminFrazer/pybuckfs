#!/usr/bin/env python3
from __future__ import annotations
from .object import Object
from .localObject import LocalObject
from typing import List, Union
from abc import ABC
from pathlib import Path
# from abc import abstractmethod
from typing import overload
from typing import TypeVar, Generic
from .bfs import BFS
import pandas as pd

T = TypeVar('T')


class ObjectCollection(ABC, Generic[T]):
    """Container for working with multiple objects."""

    # parameters that objects may be
    _object_parameters: list = [
                        "type",  # local, AWS, GoogleDrive
                        "uuid",  # uuid of the object
                        "bucket",  # name of the bucket to which item belongs
                        "id",  # unique identifier of the instance (e.g path)
    ]
    # _object = List[Object]
    _objects = pd.DataFrame()
    _bfs: BFS

    def __init__(self, object_df: pd.Dataframe = None) -> None:
        """Initialise ObjectCollection class."""
        # create an empty dataframe
        if object_df is None:
            self._objects = pd.DataFrame(columns=self._object_parameters)
        else:
            self._objects = object_df
        self._bfs = BFS()

    def filter(self, **filters) -> ObjectCollection:
        """Filter contained objects."""
        # validate filters
        not_allowed = set(filters).difference(self._object_parameters)
        if len(not_allowed) > 0:
            raise ValueError(f"filter(s) not allowed: {not_allowed}")

        for key, val in filters.items():
            self._objects = self._objects[self._objects[key] == val]

    @overload
    def __getitem__(self, key: slice) -> ObjectCollection[T]: ...
    @overload
    def __getitem__(self, key: int) -> T: ...

    def __getitem__(self, key: Union[int, slice]) -> Union[ObjectCollection(), T]:
        """Return nth object in collection."""
        if isinstance(key, slice):
            # Get the start, stop, and step from the slice
            df = self._objects.iloc[key]
            return ObjectCollection(df)
        elif isinstance(key, int):
            if key < 0:  # Handle negative indices
                key += len(self)
            if key < 0 or key >= len(self):
                raise IndexError(f"The index {key} is out of range.")
            return self._objects.iloc[key]
        else:
            raise TypeError("Invalid argument type.")

    def __len__(self):
        """Return the length of the collection."""
        return len(self._objects.shape[0])

    def __str__(self) -> str:
        """Str of class."""
        return str(self._objects)

    def __repr__(self) -> str:
        """Representation of class."""
        return repr(self._objects)


class Dir(ObjectCollection):
    """Object collection from a directory."""

    _path: Path

    def __init__(self, path: str) -> None:
        """Initialise Dir class."""
        if not self._path.exists():
            raise ValueError(f"Path not found: {str(path)}")
        if not self._path.is_dir():
            raise ValueError(f"Path is not a directory: {str(path)}")
        self._path = Path(path)

    def _get_all_files(self, path: str) -> List[str]:
        """Return all files in under the path."""
        # convert list of paths into newline seperated str
        all_files = list(Path(".").rglob("*"))
        all_files = "\n".join(all_files)
        # get the regex
        re = self._bfs.get_uuid_re()
        # run regex on list of all files
        files_list = re.findall(all_files)

        for this_item in files_list:
            full_path = this_item[0]
            uuid = this_item[1]
            obj = LocalObject(full_path, uuid)
