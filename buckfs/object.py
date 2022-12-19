#!/usr/bin/env python3
from abc import ABC, abstractmethod, abstractproperty
from .bucket import Bucket


class Object(ABC):
    """Abstract base class representing an individual instance of an object."""

    def __init__(self):
        """Initialize Object."""
        raise NotImplementedError

    @abstractmethod
    def get_hash(self):
        """Return the hash (usualy md5) of the object."""
        raise NotImplementedError

    @abstractmethod
    def get_tmodified(self) -> int:
        """Return the last time this object."""
        raise NotImplementedError

    @abstractmethod
    def is_dir(self) -> bool:
        """Return true if object represents a directory."""
        raise NotImplementedError

    @abstractmethod
    def get_bucket(self) -> Bucket:
        """Return the bucket that this object belongs to."""
        raise NotImplementedError

