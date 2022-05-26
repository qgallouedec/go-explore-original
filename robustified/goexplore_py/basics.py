# Copyright (c) 2020 Uber Technologies, Inc.

# Licensed under the Uber Non-Commercial License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at the root directory of this project.

# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import bz2
import collections
import copy
import functools
import gc
import glob
import gzip as gz
import hashlib
import heapq
import itertools
import json
import multiprocessing
import os
import pickle
import random
import shutil
import sys
import time
import typing
import uuid
import warnings as _warnings
from collections import Counter, defaultdict, namedtuple
from pathlib import Path

import loky


def fastdump(data, file):
    pickler = pickle.Pickler(file)
    pickler.fast = True
    pickler.dump(data)


import enum
from contextlib import contextmanager
from enum import Enum, IntEnum

try:
    from dataclasses import dataclass
    from dataclasses import field as datafield

    def copyfield(data):
        return datafield(default_factory=lambda: copy.deepcopy(data))

except Exception:
    _warnings.warn("dataclasses not found. To get it, use Python 3.7 or pip install dataclasses")

infinity = float("inf")


def notebook_max_width():
    from IPython.core.display import HTML, display

    display(HTML("<style>.container { width:100% !important; }</style>"))


class memoized(object):
    """Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)
