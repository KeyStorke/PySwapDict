# for swap dict
from hashlib import md5
from threading import Semaphore
from multiprocessing import Lock
from multiprocessing import Manager
# for context manager
import os
import shelve


class ContextManager:
    """ Context manager for IO operations for dict-file
    """

    def __init__(self, swap_filename, delete_file, lock, semaphore):
        self.swap_filename = swap_filename
        # checking exists swap_file and removing him
        if os.path.isfile(self.swap_filename):
            if delete_file:
                os.remove(self.swap_filename)
            else:
                raise SystemError
        self.file_instance = shelve.open(self.swap_filename)
        self.file_instance.close()
        # init mutex for multithreading
        self.semaphore = semaphore
        # init lock for multiprocessing
        self.lock = lock

    def __enter__(self):
        self.semaphore.acquire()
        self.lock.acquire()
        self.file_instance = shelve.open(self.swap_filename)
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
    1. swap_filename - swap swap_file name
    2. delete_file - status of delete swap_file if him exists
    3. lock - multiprocessing.Lock() for safe multiprocessing work
    3. semaphore - threading.Semaphore() for safe mulithreading work
    """

    def __init__(
        self,
        swap_filename='swap_dict',
        delete_file=True,
        lock=Lock(),
        semaphore=Semaphore(),
    ):

        # for sync multi- processing/threading

        self.semaphore = semaphore
        self.lock = lock

        # for safe multiprocessing

        self.cm = ContextManager(swap_filename=swap_filename,
                                 delete_file=delete_file,
                                 semaphore=self.semaphore,
                                 lock=self.lock)

        self.manager = Manager()

        # init thread-safe list

        self.int_keys = self.manager.dict()

    def __setitem__(self, key, value):
        with self.cm as swap_file:
            if type(key) == int:

                # calculate checksum

                hash = md5(str(key).encode()).hexdigest()

                # remember hash

                if hash not in self.int_keys:
                    self.int_keys[hash] = key

                # add to dict-file

                swap_file[hash] = value
            else:
                swap_file[key] = value

    def __getitem__(self, key):
        value = None
        with self.cm as swap_file:
            if type(key) == int:
                hash = md5(str(key)).hexdigest()
                if hash not in self.int_keys:
                    raise KeyError
                value = swap_file[hash]
            else:
                value = swap_file[key]
        return value

    def __str__(self):
        with self.cm as swap_file:
            value = str(swap_file)
        return value

    def __len__(self):
        with self.cm as swap_file:
            value = len(swap_file)
        return value

    def __iter__(self):
        value = dict()
        with self.cm as swap_file:
            keys = swap_file.keys()
            values = swap_file.values()
            ret = map(lambda k, v: value.update({k: v}), keys,
                      values).__iter__()
        return ret

    def __missing__(self, key):
        with self.cm as swap_file:
            value = swap_file.__missing__(key)
        return value

    def __delitem__(self, key):
        with self.cm as swap_file:
            if type(key) == int:
                hash = md5(str(key)).hexdigest()
                if hash not in self.int_keys:
                    raise KeyError
                del self.int_keys[hash]
                del swap_file[hash]
            else:
                del swap_file[key]

    def values(self):
        """ Return the list of values """
        values = list()
        with self.cm as swap_file:
            values = list(swap_file.values())
        return values

    def keys(self):
        """ Return the list of keys """
        pseudo_keys = list()
        keys = list()
        with self.cm as swap_file:
            pseudo_keys = swap_file.keys()
            for key in pseudo_keys:
                if key in self.int_keys.keys():
                    keys.append(self.int_keys[key])
                else:
                    keys.append(key)
        return keys
