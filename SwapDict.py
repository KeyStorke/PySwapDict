#!/usr/bin/python
# -*- coding: utf-8 -*-
# for swap dict

from hashlib import md5
from threading import Semaphore
from multiprocessing import Lock
from multiprocessing import freeze_support
from multiprocessing import Manager
import sys

# for logging

import logging
from logging import INFO
from logging import DEBUG

# for context manager

import os
import shelve

# for random string

import random
import string


def rand_string(length=10):
    """ Generate and return random string
    Args:
    1. length - length of random string
    """
    return ''.join(random.choice(string.digits + string.ascii_lowercase +
                   string.ascii_uppercase) for i in range(length))


class ContextManager:

    """ Context manager for IO operations for dict-file
    """

    def __init__(self, filename, delete_file, lock, semaphore):
        self.filename = filename

        # checking exists file and removing him

        if os.path.isfile(self.filename):
            if delete_file:
                os.remove(self.filename)
            else:
                raise SystemError
        self.file_instance = shelve.open(self.filename)
        self.file_instance.close()

        # init mutex for multithreading

        self.semaphore = semaphore

        # init lock for multiprocessing

        self.lock = lock

    def __enter__(self):
        self.semaphore.acquire()
        self.lock.acquire()
        self.file_instance = shelve.open(self.filename)
        return self.file_instance

    def __exit__(self, *args):
        self.file_instance.close()
        self.lock.release()
        self.semaphore.release()


class SwapDict:

    """ Classic python dict() with swap data into disk space
    Features:
    1. safe multithreading and multiprocessing
    2. swap data into disk space
    Args:
    1. filename - swap file name
    2. delete_file - status of delete file if him exists
    3. lock - multiprocessing.Lock() for safe multiprocessing work
    3. semaphore - threading.Semaphore() for safe mulithreading work
    """

    def __init__(self, filename=None, delete_file=True, lock=None,
                 semaphore=None, manager=None):
        self.swap_filename = (filename if filename else rand_string())

        # for sync multi- processing/threading

        freeze_support()
        self.semaphore = (semaphore if semaphore else Semaphore())
        self.lock = (lock if lock else Lock())

        # for safe multiprocessing

        self.cm = ContextManager(filename=self.swap_filename,
                                 delete_file=delete_file,
                                 semaphore=self.semaphore,
                                 lock=self.lock)
        # setup logging

        myhandler = logging.StreamHandler()
        myformatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        myhandler.setFormatter(myformatter)
        self.logger = logging.getLogger(name=__name__)
        self.logger.addHandler(myhandler)
        self.logger.setLevel(INFO)

        if not hasattr(sys, "_MEIPASS") and not manager:
            manager = Manager()

        if manager:
            self.logger.debug('INIT SWAP DICT WITH MANAGER!')
        else:
            self.logger.debug('INIT SWAP DICT WITHOUT MANAGER!')

        self.manager = (manager if manager else None)

        # init thread-safe list or simple list

        self.int_keys = \
            (self.manager.dict() if self.manager else dict())

    def __del__(self):
        os.remove(self.swap_filename)

    def __setitem__(self, key, value):
        with self.cm as file:
            if isinstance(key, int):

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
                hash = md5(str(key)).hexdigest()
                if hash not in self.int_keys:
                    self.logger.debug("KeyError with %s", str(key))
                    raise KeyError
                value = file[hash]
            else:
                value = file[key]
        return value

    def __str__(self):
        with self.cm as file:
            value = str(file)
        return value

    def __len__(self):
        with self.cm as file:
            value = len(file)
        return value

    def __iter__(self):
        return dict(zip(self.keys(), self.values())).__iter__()

    def __missing__(self, key):
        with self.cm as file:
            value = file.__missing__(key)
        return value

    def __delitem__(self, key):
        with self.cm as file:
            if type(key) == int:
                hash = md5(str(key)).hexdigest()
                if hash not in self.int_keys:
                    self.logger.debug("KeyError with %s", str(key))
                    raise KeyError
                del self.int_keys[self.int_keys.index(hash)]
                del file[hash]
            else:
                del file[key]

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
