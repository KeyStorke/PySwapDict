# About

Python swap-dictionary. Standard python class, with dict-like interface. Support:
 * iteration, updating, creation from standard dictionary
 * swapping data to disk space
 * safe multiprocess/multithread work
 * support build with Pyinstaller
 * Python 2.7 or higher  (including 3.5)
 * creation SwapDict from standard dictionary
 
# Example:

```python
from SwapDict import SwapDict

d = SwapDict()

for i in range(0, 20):
    d[i] = str(i)
```

# TODO

- [ ] Create ContextManager without shelve (and him bugs!)

