#!/usr/bin/python2
# -*- coding: utf-8 -*-
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

# for tests

import unittest
import threading


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
        self.__context_couner = 0

    def __enter__(self):
        self.semaphore.acquire()
        self.lock.acquire()
        self.__context_couner += 1
        if self.__context_couner == 1:
            self.__file_instance = shelve.open(self.filename)
        return self.__file_instance

    def __exit__(self, *args):
        self.__context_couner -= 1
        if self.__context_couner == 0:
            self.__file_instance.close()
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
            if isinstance(key, int):
                hash = md5(str(key).encode()).hexdigest()
                if hash not in self.int_keys:
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
            if isinstance(key, int):
                hash = md5(str(key)).hexdigest()
                if hash not in self.int_keys:
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
        keys = list()
        with self.cm as file:
            pseudo_keys = file.keys()
            for key in pseudo_keys:
                if key in self.int_keys.keys():
                    keys.append(self.int_keys[key])
                else:
                    keys.append(key)
        return keys


class __Tests(unittest.TestCase):
    def test_keys_dict(self):
        """ Testing method SwapDict.keys()
        """
        d = SwapDict(delete_file=True)
        for i in range(0, 10):
            d[i] = str(i)

        self.assertEqual(sorted(d.keys()), sorted([x for x in range(0, 10)]),
                         "Error in method __setitem__() or keys()")

    def test_values_dict(self):
        """ Testing method SwapDict.values()
        """
        d = SwapDict(delete_file=True)
        for i in range(0, 10):
            d[i] = str(i)

        self.assertEqual(sorted(d.values()), sorted([str(x) for x in range(0, 10)]),
                         "Error in method __setitem__() or values()")

    def test_len_dict(self):
        """ Testing method SwapDict.__len__()
        """
        d = SwapDict(delete_file=True)
        for i in range(0, 10):
            d[i] = str(i)

        self.assertTrue(len(d) == 10, "Error mehod __len__()")

    def test_setitem_dict(self):
        """ Testing method SwapDict.__setitem__()
        """
        d = SwapDict(delete_file=True)
        for i in range(0, 10):
            d[i] = str(i)

        for key in d:
            self.assertTrue(key == int(d[key]), "Error in method __setitem__() \n"
                                                "key: %s, value: %s" % (str(key), d[key]))

    def test_multithreading_creation_dict(self):
        """ Testing multithreading creation dict

        :return:
        """
        # for sync
        semaphore = Semaphore()
        lock = Lock()

        d = SwapDict(
            delete_file=True,
            lock=lock,
            semaphore=semaphore,
        )

        # first process
        def first():
            for i in range(10, 21):
                d[i] = i + 1

        # second process
        def second():
            for i in range(0, 11):
                d[i] = i + 2

        # init thread
        t1 = threading.Thread(target=first)
        t2 = threading.Thread(target=second)

        # starting process
        t1.start()
        t2.start()

        # wait for process
        t1.join()
        t2.join()

        self.assertFalse(len(d) != 21, "Error creaion dict, check SyncManager")

        for key in d:
            self.assertFalse(d[key] - key != 1 and d[key] - key != 2, "multiprocess creation dict error!")

    def test_multithreading_read_dict(self):
        """ Testing multithreading creation dict

            :return:
            """
        # for sync
        semaphore = Semaphore()
        lock = Lock()

        d = SwapDict(
            delete_file=True,
            lock=lock,
            semaphore=semaphore,
        )

        for i in range(0, 10):
            d[i] = i

        # first process
        def first():
            for i in d:
                # print("from first thread: key = %s, value = %s" % (i, d[i]))
                d[i] += 1

        # second process
        def second():
            for i in d:
                # print("from second thread: key = %s, value = %s" % (i, d[i]))
                d[i] += 2

        # init thread
        t1 = threading.Thread(target=first)
        t2 = threading.Thread(target=second)

        # starting process
        t1.start()
        t2.start()

        # wait for process
        t1.join()
        t2.join()

        self.assertFalse(len(d) != 10, "Error creation dict, check SyncManager")

        for key in d:
            self.assertTrue(key == d[key]-3, "Error multithreading reading dict")


if __name__ == "__main__":
    unittest.main()
