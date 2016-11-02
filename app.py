#!/usr/bin/python
# -*- coding: utf-8 -*-

from hashlib import md5
from cm import ContextManager
from threading import Semaphore
from multiprocessing import Lock
from multiprocessing import Manager


class SwapDict(dict):

    """ Classic python dict() with swap data into disk space
    Features:
    1. safe multithreading and multiprocessing
    2. swap data into disk space

    Args:
    1. filename - swap file name
    2. delete_file - status of delete file is him exists
    3. lock - multiprocessing.Lock() for safe multiprocessing work
    3. semaphore - hreading.Semaphore() for safe mulithreading work
    """

    def __init__(
        self,
        filename='swap_dict',
        delete_file=True,
        lock=Lock(),
        semaphore=Semaphore(),
    ):

        # for sync multi- processing/threading

        self.semaphore = semaphore
        self.lock = lock

        # for safe multiprocessing

        self.cm = ContextManager(filename=filename,
                                 delete_file=delete_file,
                                 semaphore=self.semaphore,
                                 lock=self.lock)

        self.manager = Manager()

        # init thread-safe list

        self.int_keys = self.manager.dict()

    def __setitem__(self, key, value):
        with self.cm as file:
            if type(key) == int:

                # calculate checksum

                hash = md5(str(key).encode()).hexdigest()

                # remember hash

                if hash not in self.int_keys:
                    self.int_keys[hash] = key

                # add to dict-file

                file[hash] = value
            else:
                file[key] = value

    def __getitem__(self, key):
        value = None
        with self.cm as file:
            if type(key) == int:
                hash = md5.md5(str(key)).hexdigest()
                if hash not in self.int_keys:
                    raise KeyError
                value = file[hash]
            value = file[key]
        return value

    def __str__(self):
        with self.cm as file:
            value = str(file)
        return value

    def __len__(self):
        with self.cm as file:
            value = len(self.file)
        return value

    def __iter__(self):
        value = dict()
        with self.cm as file:
            keys = file.keys()
            values = file.values()
            ret = map(lambda k, v: value.update({k: v}), keys,
                      values).__iter__()
        return ret

    def __length_hint__(self):
        with self.cm as file:
            value = self.file.__length_hint__()
        return value

    def __missing__(self, key):
        with self.cm as file:
            value = self.file.__missing__(key)
        return value

    def __delitem__(self, key):
        with self.cm as file:
            if type(key) == int:
                hash = md5.md5(str(key)).hexdigest()
                if hash not in self.int_keys:
                    raise KeyError
                del self.int_keys[self.int_keys.index(hash)]
                del file[hash]

    def values(self):
        values = list()
        with self.cm as file:
            values = list(file.values())
        return values

    def keys(self):
        pseudo_keys = list()
        keys = list()
        with self.cm as file:
            pseudo_keys = file.keys()
            for key in pseudo_keys:
                if key in self.int_keys.keys():
                    keys.append(self.int_keys[key])
                else:
                    keys.append(key)
        return keys
