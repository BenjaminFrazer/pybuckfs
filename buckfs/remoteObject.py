#!/usr/bin/env python3
from abc import ABC, abstractmethod, abstractproperty
from remote import Remote
from object import Object


class RemoteObject():
    """Represents a remote version of an object."""

    _remote: Remote  # Details about the remote

    def __init__(self, remote: Remote, uuid: str):
        """Initialise the RemoteObject class."""
        pass

    @abstractproperty
    def tmodified():
        """Returnlast time the file was modified on the server."""
        pass

    @abstractmethod
    def check_equal(self, obj: Object) -> bool:
        """Check if the objects matches self."""
        raise NotImplementedError
