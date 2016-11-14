import unittest
import threading
from SwapDict import SwapDict
from threading import Semaphore
from multiprocessing import Lock


class Tests(unittest.TestCase):
    def test_keys_dict(self):
        """ Testing method SwapDict.keys()
        """
        d = SwapDict(delete_file=True)
        for i in range(0, 10):
            d[i] = str(i)

        self.assertEqual(sorted(d.keys()), sorted([x for x in range(0, 10)]),
                         "Error in method __setitem__() or keys()")
        del d

    def test_values_dict(self):
        """ Testing method SwapDict.values()
        """
        d = SwapDict(delete_file=True)
        for i in range(0, 10):
            d[i] = str(i)

        self.assertEqual(sorted(d.values()), sorted([str(x) for x in range(0, 10)]),
                         "Error in method __setitem__() or values()")
        del d

    def test_len_dict(self):
        """ Testing method SwapDict.__len__()
        """
        d = SwapDict(delete_file=True)
        for i in range(0, 10):
            d[i] = str(i)

        self.assertTrue(len(d) == 10, "Error method __len__()")
        del d

    def test_setitem_dict(self):
        """ Testing method SwapDict.__setitem__()
        """
        d = SwapDict(delete_file=True)
        for i in range(0, 10):
            d[i] = str(i)

        for key in d:
            self.assertTrue(key == int(d[key]), "Error in method __setitem__() \n"
                                                "key: %s, value: %s" % (str(key), d[key]))
        del d

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

        self.assertFalse(len(d) != 21, "Error creation dict, check SyncManager")

        for key in d:
            self.assertFalse(d[key] - key != 1 and d[key] - key != 2, "multiprocess creation dict error!")
        del d

    def test_creation_dict_from_std_dict(self):
        """ Testing creation SwapDict from standard dict

        :return:
        """
        semaphore = Semaphore()
        lock = Lock()

        std_dict = {'a': 1, 'b': 2, 'c': 3}

        d = SwapDict(std_dict)
        self.assertTrue(str(sorted(d)) == str(sorted(std_dict)), "Error creation SwapDict from dict, info: \nSwapDict: %s\n dict: %s" %
                        (str(d), str(std_dict)))
        del d

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
            dictionary=dict(zip(range(0, 10), range(0, 10)))
        )

        # first process
        def first():
            for first_key in d:
                # print("from first thread: key = %s, value = %s" % (i, d[i]))
                d[first_key] += 1

        # second process
        def second():
            for second_key in d:
                # print("from second thread: key = %s, value = %s" % (i, d[i]))
                d[second_key] += 2

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
        del d

if __name__ == "__main__":
    unittest.main()
