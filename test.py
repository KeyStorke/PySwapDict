#!/usr/bin/python2
from app import SwapDict
from multiprocessing import Process
from multiprocessing import Lock
from threading import Semaphore
import os

if os.path.isfile('test'):
    os.remove('test')

# for sync

semaphore = Semaphore()
lock = Lock()

d = SwapDict(
    filename='test',
    delete_file=False,
    lock=lock,
    semaphore=semaphore,
    )


def first():
    for i in range(0, 20):
        d[i] = i+1


def second():
    for i in range(0, 20):
        d[19-i] = 19 - i+2

p1 = Process(target=first)
p2 = Process(target=second)

p1.start()
p2.start()

p1.join()
p2.join()

for i in d.values():
    pass

for i in d.keys():
    pass

for value, key in zip(d.values(), d.keys()):
    if value - key == 1:
        print(str(key) + str(" + 1 = ") + str(value))
    else:
        print(str(key) + str(" + 2 = ") + str(value))

print(len(d.int_keys))
assert len(d.int_keys) == 20
