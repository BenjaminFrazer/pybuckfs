#!/usr/bin/env python3
from abc import ABC, abstractmethod, abstractproperty
import pandas as pd
from typing import List
from typing import Dict
import yaml



class Remote(ABC):
    """Abstract base class for syncing remote buckets."""
    _bucket_name: str = "Not Set"

    @abstractproperty
    def bucket(self):
        pass
