from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout

from source.posterior.core.instmodel4dataset import Instmodel4Dataset
from source.tools.lockable_dict import Lock
# from ipdb import set_trace


level_logger = DEBUG
level_handler = INFO

logger = getLogger()
if logger.level != level_logger:
    logger.setLevel(level_logger)
if len(logger.handlers) == 0:
    ch = StreamHandler(stdout)
    ch.setLevel(level_handler)
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
else:
    ch = logger.handlers[0]
    if ch.level != level_handler:
        ch.setLevel(level_handler)


class TestMethods(TestCase):

    def setUp(self):
        Instmodel4Dataset()

    def test_copy(self):
        lck = Lock()
        i4d = Instmodel4Dataset(list_datasetnames=["dataset1", "dataset2"], lock=lck)
        i4d["dataset1"] = "instmodel1"
        i4d["dataset2"] = "instmodel2"
        i4d_copy = i4d.copy()
        print("i4d: {}\ni4d_copy: {}".format(i4d, i4d_copy))
        print("lock i4d: {}\nlock i4d_copy: {}".format(i4d.get_Lock_instance(),
                                                       i4d_copy.get_Lock_instance()))
        self.assertTrue(i4d.get_Lock_instance() is lck)
        self.assertFalse(i4d_copy.get_Lock_instance() is lck)


if __name__ == '__main__':
    main()
