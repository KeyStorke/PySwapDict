#!/usr/bin/python2
# -*- coding: utf-8 -*-
""" Module PySwapDict implement python dictionary with automatically swap data to disk space


"""
# for swap dict

from hashlib import md5
from threading import Semaphore
from multiprocessing import Lock
from multiprocessing import Manager
import sys

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
                                 string.ascii_uppercase) for simbol in range(length))


class ContextManager:
    """ Context manager for IO operations for dict-file
    """

    def __init__(self, filename, lock, semaphore, delete_file=True):
        self.filename = filename

        # checking exists file and removing him

        if os.path.isfile(self.filename):
            if delete_file:
                os.remove(self.filename)
            else:
                raise SystemError
        self.__file_instance = shelve.open(self.filename)
        self.__file_instance.close()

        # init mutex for multithreading

        self.semaphore = semaphore

        # init lock for multiprocessing

        self.lock = lock

        # counter call context
        self.__context_counter = 0

    def __enter__(self):
        self.semaphore.acquire()
        self.lock.acquire()
        self.__context_counter += 1
        if self.__context_counter == 1:
            self.__file_instance = shelve.open(self.filename)
        return self.__file_instance

    def __exit__(self, *args):
        self.__context_counter -= 1
        if self.__context_counter == 0:
            self.__file_instance.close()
        self.lock.release()
        self.semaphore.release()


class SwapDict(object):
    """ Classic python dict() with swap data into disk space
    Features:
    1. safe multithreading and multiprocessing
    2. swap data into disk space
    Args:
    1. filename - swap file name
    2. delete_file - status of delete file if him exists
    3. lock - multiprocessing.Lock() for safe multiprocessing work
    3. semaphore - threading.Semaphore() for safe multithreading work
    """

    def __init__(self, dictionary = None, filename=None, delete_file=True, lock=None,
                 semaphore=None, manager=None, *args):
        self.swap_filename = str(filename if filename is not None else rand_string())

        # for sync multi- processing/threading

        self.semaphore = (semaphore if semaphore is not None else Semaphore())
        self.lock = (lock if lock is not None else Lock())

        # for safe multiprocessing

        self.cm = ContextManager(filename=self.swap_filename,
                                 delete_file=delete_file,
                                 semaphore=self.semaphore,
                                 lock=self.lock)

        # checking for pyinstaller

        if not hasattr(sys, "_MEIPASS") and manager is None and (
                "win" not in sys.platform and sys.platform != "darwin"):
            # pyinstaller not detected, create SyncManager
            manager = Manager()

        self.manager = (manager if manager is not None else None)

        # init thread-safe list or simple list

        self.int_keys = \
            (self.manager.dict() if self.manager else dict())

        if dictionary is not None:
            for key in dictionary:
                self.__setitem__(key=key, value=dictionary[key])
        else:
            for arg in args:
                if isinstance(arg, dict):
                    for key in arg:
                        self.__setitem__(key=key, value=arg[key])


    def __del__(self):
        # under linux created one file, under windows - 3
        for filename in os.listdir(os.path.expanduser(".")):
            if filename.split(".")[0] == self.swap_filename:
                try:
                    os.remove(filename)
                except FileNotFoundError:
                    pass

    def __setitem__(self, key, value):
        with self.cm as file:
            if not isinstance(key, str):

                # calculate checksum

                key_hash = md5(str(key).encode()).hexdigest()

                # remember hash

                if key_hash not in self.int_keys:
                    self.int_keys[key_hash] = key

                # add to dict-file

                file[key_hash] = value
            else:
                file[key] = value

    def __getitem__(self, key):
        value = None
        with self.cm as file:
            if isinstance(key, int):
                key_hash = md5(str(key).encode()).hexdigest()
                if key_hash not in self.int_keys:
                    raise KeyError
                value = file[key_hash]
            else:
                value = file[key]
        return value

    def __str__(self):
        return dict(zip(self.keys(), self.values())).__str__()

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
            if isinstance(key, int):
                key_hash = md5(str(key)).hexdigest()
                if key_hash not in self.int_keys:
                    raise KeyError
                del self.int_keys[self.int_keys.index(key_hash)]
                del file[key_hash]
            else:
                del file[key]

    def __repr__(self):
        return dict(zip(self.keys(), self.values())).__repr__()

    def values(self):
        with self.cm as file:
            values = list(file.values())
        return values

    def keys(self):
        keys = list()
        with self.cm as file:
            pseudo_keys = file.keys()
            for key in pseudo_keys:
                if key in self.int_keys.keys():
                    keys.append(self.int_keys[key])
                else:
                    keys.append(key)
        return keys
