"""Implement the BFS class."""
# from abc import ABC, abstractmethod, abstractproperty
# import pandas as pd
# from typing import List
import os
from pathlib import Path
from typing import Dict, List
import yaml
from .bucket import Bucket
import re
from typing import Pattern
from warnings import warn
import shortuuid


class ConfigParseError(Exception):
    """Descriptive exception for failure in config parse."""

    pass


class BFS:
    """Common buck fs settings and tools."""

    _buckets: Dict[str, Bucket] = {}  # All of the buckets present on the
    _config_dir: str  # where are the configuration files
    _uuid_re: Pattern  # regular expression for matching uuids
    _re_inited: bool = False  # have we initialised the regex
    _config_file_path: Path  # file path to the current configuration file
    # places to look for the buckfs yaml file
    _config_file_default_locations: List[str] =\
        ["~/.config/buckfs/buckfs.yaml"]
    _uuid_dict: str  # dictionary of uuids
    _short_uuid_init: bool = False  # have we initialised short uuid
    _uuid_len: int = 12
    # TODO hard code for now will turn into a property that serches later

    def __init__(self, *args, **kwargs):
        """Initialise buckfs."""
        # we need to parse the config section dir to find all of the remotes
        # if they are defined.
        if len(args) > 0:
            if not isinstance(args[0], str):
                raise ValueError("First argument \"config_path\" must be a string.")
            str_path = args[0]
        else:
            str_path = kwargs.get("config_path", None)
        if str_path is None:
            # we don't have a valid path string from args
            self._config_file_path = self._find_config_file_in_default_loc()
        else:
            # we have a valid path string from args
            self._config_file_path = Path(str_path).expanduser()
            if not self._config_file_path.exists():
                raise ValueError(f"Path doen't exit: {str(str_path)}")
        # parse the config file
        self._parse_config_file()
        # build the regular expression used to match file names
        self._build_re()

    def _parse_config_file(self):
        # hardcoded yaml file location for now
        with self.config_file_path.open() as f:
            config = yaml.safe_load(f)
        buckets_dict = config.get("buckets", None)
        if buckets_dict is None:
            raise ConfigParseError("Can't find any buckets.")
        # loop through all of the buckets
        for bucket_name in buckets_dict:
            this_bucket_dict = buckets_dict[bucket_name]
            paths = this_bucket_dict.get("dirs", None)
            if paths is None:
                raise ConfigParseError("Bucket must have at least one"
                                       "entry under \"dirs\".")
            remote = this_bucket_dict.get("remote", None)
            name = this_bucket_dict.get("name", None)
            self._buckets[bucket_name] = Bucket(paths, name, remote)

            # extract the uuid dictionary
            uuid_alph = this_bucket_dict.get("uuid_alphabet", None)
            if uuid_alph is None:
                uuid_alph = shortuuid.get_alphabet()
            found_blocklist_chars = self._find_blocklist_chars(uuid_alph)
            if len(found_blocklist_chars) > 0:
                raise ConfigParseError("UUID alphabet contained "
                                       "forbidden characters!\n"
                                       f"{found_blocklist_chars}")
            self._uuid_alphabet = uuid_alph
            # extract the uuid length
            uuid_len = this_bucket_dict.get("uuid_len", None)
            if uuid_len is not None:
                self._uuid_len = uuid_len

    # TODO currently this does nothing
    def _find_config_file_in_default_loc(self) -> Path:
        """Return config file path."""
        for path in self._config_file_default_locations:
            f = Path(path)
            if f.exists():
                return f
        raise FileNotFoundError("No config file found in default locations.")

    @property
    def config_file_path(self) -> Path:
        """Return path to the currently inuse config file."""
        return self._config_file_path

    def gen_uuid(self, length: int = None) -> str:
        r"""Generate a UUID."""
        if length is None:
            length = self._uuid_len
        if not self._short_uuid_init:
            shortuuid.set_alphabet(self._uuid_alphabet)
        return shortuuid.uuid()[:length]

    def _build_re(self):
        """Build regular expression used to match uuid in file name string."""
        re_path = r"(?:[ a-zA-Z0-9_\-\/.]*\/)?"
        re_name = r"(?:[ a-zA-Z0-9_\-\[\]]*)"
        re_extention = r"(?:[.][a-zA-z]{1,4})?"
        escaped_alphabet = self._escape_regex_chars(self._uuid_alphabet)
        re_uuid = r"\[(" f"[{escaped_alphabet}]" r"{3,12})\]"
        uuid_re = f'^{re_path}{re_name}{re_uuid}{re_extention}$'
        self._re_inited = True
        # self._uuid_re_comp = re.compile(uuid_re, re.MULTILINE)
        self._uuid_re = re.compile(uuid_re)

    def _escape_regex_chars(self, chars: str):
        """Properly escape these chars if detected."""
        if not type(chars) is str:
            raise ValueError(f"Type: {type(chars)} not supported.")
        uuid_chars_2_escape = ["-", "\\", "?", "[",
                               "]",  "(",  ")", ".",
                               "*", "$", "^"]
        return ''.join('\\'+char if char in uuid_chars_2_escape else char
                       for char in chars)

    def _find_blocklist_chars(self, alphabet: str):
        """Check alphabet contains only valid characters."""
        uuid_blocklist_chars = set(
                               ["[",  "]",  ")", "(",
                                "/", "\\", "\"", "*",
                                "%",  "+",  "=", "^",
                                "£",  "$",  "!", "?",
                                "`",  "@",  "~", "#",
                                "'",  " "])
        alphabet_set = set(*[alphabet])
        return uuid_blocklist_chars.intersection(alphabet_set)

    def get_uuid_re(self) -> Pattern:
        """Return regular expression for finding uuids in file names/paths."""
        if not self._re_inited:
            self._build_re()
        return self._uuid_re

    def parse_uuid(self, path: Path, throw: bool = True) -> str:
        """Return the uuid from filepath."""
        if not (type(path) is str or isinstance(path, Path)):
            msg = f"path should be either a str or a pathlib.Path,\
            instead: {type(path)}"
            if throw:
                raise ValueError(msg)
            else:
                warn(msg)
        if type(path) is str:
            path = Path(path)

        if not path.exists():
            warn(f"path not found: \"{path.absolute()}\"")

        re = self.get_uuid_re()
        uuid_ls = re.findall(path.name)
        if len(uuid_ls) != 1:
            msg = f"uuid couldn't be parsed from: {path.str()}"
            if throw:
                raise ValueError(msg)
            else:
                warn(msg)
                return None
        else:
            return uuid_ls[0]

    @property
    def buckets(self) -> Dict[str, Bucket]:
        """Return all buckets currently tracked."""
        return self._buckets

    def get_parents(self, path: str) -> List[Path]:
        """
        Return the parent directories of the current path as a list.

        The last element is always root or C:/ in windows.
        """
        from pathlib import Path
        path = Path("~/repos/buckfs/buckfs/bfs.py")
        parents = [p for p in path.expanduser().parents]
        parents.insert(0, path)

    def get_bucket_from_path(self, path: str) -> Bucket:
        """
        Return the root directory for any given path.

        This is not necicerily a tracked directory though it can be, it is
        simply a directory which is pointed to in the .yaml
        Throws an error if no root directory can be found. Root
        will always be marked as
        """
        path_parents = self.get_parents(path)

        # loop to check if any of the roots match a parent of
        found = False
        for name, bucket in self._buckets.items():
            for root in bucket.get_roots():
                root = Path(root).resolve()
                for parent in path_parents:
                    if root == parent.resolve():
                        found = True
                        break
        if found is False:
            raise ValueError("Cannot find {path} under any bucket roots.")
        return bucket

    def track_file(self, filepath: str):
        """Take an exhisting file and insert a new UUID."""
        # sanity checks
        fp = Path(filepath).expanduser()
        if not fp.exists():
            raise ValueError(f"File: {fp.str()} not found.")
        if self.parse_uuid(fp, False) is not None:
            raise ValueError(f"File: {fp.str()} already contains valid uuid.")
        # test if the file is symbolic
        # TODO Review if this is required
        if fp.is_symlink():
            raise ValueError(f"File: {fp.str()} is simlink.")
        uuid = self.gen_uuid()
        stem = fp.name.split(".")[0]
        # handels multiple sufixes (eg .org.txt.cpp)
        sufixs = "".join("."+s for s in fp.name.split(".")[1:])
        dest = fp.parent + stem + f"[{uuid}]" + sufixs
        os.rename(fp, dest)


if __name__ == "__main__":
    bfs = BFS()
    fp = "~/data/test buckfs/repository to sync/a note.txt"
    bfs.track_file(fp)
