#!/usr/bin/python2
import time
import os
import shelve


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
