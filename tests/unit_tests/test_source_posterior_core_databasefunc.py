from unittest import TestCase, main
from logging import getLogger, StreamHandler, Formatter
from logging import DEBUG, INFO
from sys import stdout

from source.posterior.core.database_func import DatabaseFunc, DatabaseInstLvlDataset
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
        pass

    def test_basics_creation_DatabaseInstLvlDataset(self):
        DatabaseInstLvlDataset(object_stored="testfunc", database_name="test")

    def test_DatabaseInstLvlDataset_setgetitem(self):
        db = DatabaseInstLvlDataset(object_stored="testfunc", database_name="test")
        db.instmodel4dataset["RV_K2-19_HARPS_0"] = "default"
        db["RV"]["HARPS"]["default"] = "bingo"
        self.assertEqual(db["RV_K2-19_HARPS_0"], "bingo")

    def test_basics_creation_DatabaseFunc(self):
        DatabaseFunc(object_stored="testfunc", database_name="test")

    def test_DatabaseFunc_updateinstdb(self):
        lck_dst = Lock()
        lck_db = Lock()
        db = DatabaseFunc(object_stored="testfunc", database_name="test", lock_dataset=lck_dst,
                          lock_database=lck_db)
        self.assertTrue(db.get_dataset_Lock_instance() is lck_dst)
        self.assertTrue(db.instmodel4dataset.get_Lock_instance() is lck_dst)
        self.assertTrue(db.get_database_Lock_instance() is lck_db)
        self.assertTrue(db.instrument_db.get_database_Lock_instance() is lck_db)
        inst_db = DatabaseInstLvlDataset(object_stored="testfunc", database_name="test")
        inst_db["RV"]["HARPS"]["default"] = "bingo"
        db.instrument_db.update(inst_db)
        self.assertTrue(db.instrument_db.get_database_Lock_instance() is lck_db)
        self.assertEqual(db.instrument_db["RV"]["HARPS"]["default"], "bingo")
        self.assertTrue(db.instrument_db is not inst_db)


if __name__ == '__main__':
    main()
