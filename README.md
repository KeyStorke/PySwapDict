# About

Python swap-dictionary. Standard python class, with dict-like interface. Support:
 * iterator
 * swapping data to disk space
 * safe multiprocess/multithread work
 * support build with Pyinstaller
 * Python 2.7 or higher  (including 3.5)

# Example:

```python
from SwapDict import SwapDict

d = SwapDict()

for i in range(0, 20):
    d[i] = str(i)
```

# TODO

- [ ] Creating dict of dict-object from argument
- [ ] Create setup script
- [ ] Create ContextManager without shelve (and him bugs!)

