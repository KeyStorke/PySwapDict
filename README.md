# About

Python swap-dictionary. Standard python class, with dict-like interface. Support:
 * iterator
 * getting length
 * swapping data to disk space
 * safe multiprocess/multithread work
 * support build with Pyinstaller
 * Python 2.7 or higher  (including 3.5)

# Examples

```python
from SwapDict import SwapDict
from multiprocessing import Lock
from threading import Semaphore

d = SwapDict()

for i in range(0, 20):
    d[i] = str(i)
```

with multithreading:
```python
from SwapDict import SwapDict
from multiprocessing import Process
from multiprocessing import Lock
from threading import Semaphore

# for sync
semaphore = Semaphore()
lock = Lock()

d = SwapDict(
    filename='test',
    delete_file=True,
    lock=lock,
    semaphore=semaphore,
    )

# first process
def first():
    for i in range(0, 20):
        d[i] = i+1

# second process
def second():
    for i in range(0, 20):
        d[19-i] = 19 - i+2

# init process
p1 = Process(target=first)
p2 = Process(target=second)

# starting process
p1.start()
p2.start()


# wait for process
p1.join()
p2.join()

# print result
for key in d:
    # if inserted first process
    if d[key] - key == 1:
        print(str(key) + str(" + 1 = ") + str(d[key]))
    else:
        # if inserted second process
        print(str(key) + str(" + 2 = ") + str(d[key]))
```
