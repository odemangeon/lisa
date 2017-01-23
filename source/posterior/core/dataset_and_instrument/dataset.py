#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
dataset module.

The objective of this package is to provides the core Dataset class to store
and manipulate the data.

@DONE:
    - Dataset.__init__: Doc an UT
    - Dataset._set_filepath: Doc and UT
    - Dataset.get_filepath: Doc and UT
    - Dataset.get_filename: Doc and UT
    - Dataset._set_instrument: Doc and UT
    - Dataset.get_instrument: Doc and UT
    - Dataset._set_objectname: Doc and UT
    - Dataset.get_objectname: Doc and UT
    - Dataset._rm_data: Doc and UT
    - Dataset.is_data_loaded: Doc and UT
    - Dataset.load_data: Doc
    - Dataset._set_data: Doc and UT
    - Dataset.get_data: Doc and UT

@TODO:
    - Dataset.load_data: UT
"""
import logging
import sys
import pandas as pd

from .manager_dataset_instrument import get_filename_from_file_path, interpret_data_filename

## Logger
logger = logging.getLogger()


class Dataset(object):
    """docstring for the Dataset abstract class."""

    ## Mandatory columns: For this abstract data base there is None
    _mandatory_columns = []

    def __init__(self, file_path, instrument_instance):
        """Dataset init method FOR INHERITANCE PURPOSES (as Dataset is an abstract class).

        This __init__ does:
            1. Store the path of the data file
            2. Get the file name from the file path and interpret the file name into object name,
               instrument name and type and eventually number of the dataset
            3. Store the name of the object observed with the data
            4. Define the instrument used to take the data
            5. Initialise the data attribute
        Remarks:
            - There is no need to check for the existance of the data file because it's done by
              the Manager_Inst_Dataset class who triggers the creation of the dataset subclass
              instances
        ----
        Arguments:
            file_path           : string,
                Path of file which contains the data
            instrument_instance : Instance of a Subclass of Instrument,
                Instrument instance that describes the isntrument used to measure the data.
        Raises:
            NotImplementedError : 1 case,
                -If you try to instanciate Dataset directly.
        """
        super(Dataset, self).__init__()
        # 1.
        self._set_filepath(file_path)
        # 2.
        filename = self.get_filename()
        filename_info = interpret_data_filename(filename)
        # 3.
        self._set_objectname(filename_info["object"])
        # 4.
        self._set_instrument(instrument_instance)
        # 5.
        self._rm_data()
        # Make Dataset an abstract class
        if type(self) is Dataset:
            raise NotImplementedError("Dataset should not be instanciated!")

    def _set_filepath(self, filepath):
        """Define the path of the data file.
        ----
        Arguments:
            filepath : string,
                Path to the data file
        """
        self.__file_path = filepath

    def get_filepath(self):
        """Get the path of the data file."""
        return self.__file_path

    def get_filename(self):
        """Get the name of the data file."""
        return get_filename_from_file_path(self.get_filepath())

    def _set_instrument(self, inst_instance):
        """Define the instance of the Instrument Subclass defining the instrument used.
        ----
        instrument_instance : Instance of a Subclass of Instrument,
            Instrument instance that describes the isntrument used to measure the data.
        """
        self.__instrument = inst_instance

    def get_instrument(self):
        """Return the instrument instance.
        ----
        Returns:
            Instance of a Subclass of Instrument, Instrument instance that describes the isntrument
                used to measure the data.
        """
        return self.__instrument

    def _set_objectname(self, object_name):
        """Define the name of the object the data are about.
        ----
        Arguments:
            object_name : string,
                name of the object the data are about
        """
        self.__object_name = object_name

    def get_objectname(self):
        """Return the name of the object the data are about.
        ----
        Returns:
            object_name : string,
                name of the object the data are about
        """
        return self.__object_name

    def _rm_data(self):
        """Remove data previously loaded or initialse the data attribute."""
        self.__data = None
        logger.info("Data has been removed from {}.".format(self.get_filename()))

    def is_data_stored(self):
        """Tell if data has been stored.
        ----
        Returns:
            True is data has been loaded, False otherwise.
        """
        return self.__data is not None

    def load_data(self, store=False,
                  delim_whitespace=True,
                  skip_rows=1,
                  comment="#",
                  names="mandatory",
                  index_col=None,
                  skip_blank_lines=True,
                  header=None,
                  **kargs):
        """
        Read the light curve into a pandas database using the pandas.read_table function.

        This function does:
            1. Check if the header argument has been used. If not, it means that names should be
               used and so check if all the mandatory columns are in names. If header is used than
               change the value of names to None.
            2. Read the data file
            3. If header argument used check that the pandas dataframe contains the mandatory
               columns
            4. If inst_flag columns not provided, create one full of zeros.
            5. If store argument is True store the data in this LC_Dataset instance
            6. Return the pandas dataframe.
        ----
        Arguments:
            store            : bool, (default: False),
                If True, the data are stored in this LC_Dataset instance
            delim_whitespace : bool, (default: True),
                if True, white spaces are used as delimiters of columns
            skip_rows         : int, (default: 1),
                Number of rows to skip (after comment have been removed)
            comment           : string, (default: "#"),
                If a line starts with this character, it will be ignored
            names             : list of string, (default: ["time", "flux", "flux_err"]),
                Give the name of the columns, if your are not using the header argument.
            skip_blank_lines  : bool, (default: True),
                Ignore blank lines
            header            : Int, (default: None),
                Indicate the number of the line used as header.

        Keyword aguments:
            see documentation of pandas.read_table

        Returns:
            pandas.Dataframe instance which contains the data.

        Raise:
            ValueError : 2 cases,
                - If names is provided but doesn't include the mandatory columns given by names
                default value.
                - If header is provided but the header of the data file doesn't contain all the
                mandatory columns given by names default value.
        """
        # 1.
        header_used = header is not None
        if not header_used:
            if names == "mandatory":
                names = self._mandatory_columns
            for col_name in self._mandatory_columns:
                if col_name not in names:
                    raise ValueError("{} is a mandatory column for this Dataset subclass."
                                     "It should be included in the argument names. You provided :"
                                     "{}".format(col_name, names))
        else:
            names = None
        # 2.
        # we can also read the header from the file with
        # lc = pd.read_table('cuttransits.txt', delim_whitespace=True, header=0, index_col=0)
        pandas_df = pd.read_table(self.get_filepath(),
                                  delim_whitespace=delim_whitespace,
                                  names=names,
                                  index_col=index_col,
                                  skiprows=skip_rows,
                                  skip_blank_lines=skip_blank_lines,
                                  comment=comment,
                                  **kargs)
        # to acces the colum values lc['time'], lc['flux'], lc['flux_err']
        # they will come indexit to the time but when we transformed them into numpy
        # np.asarray(lc['inst_flag']) it is just the column
        # to have a  quick statistic summary of your data
        # lc.describe()
        # 3.
        if header_used:
            for col_name in self._mandatory_columns:
                if col_name not in pandas_df.columns:
                    raise ValueError("{} is a mandatory column for this Dataset subclass."
                                     "It should be included in the header of the data file that you"
                                     "provided. Columns provided by the header of your file: {}\n"
                                     "If this column is provided under a different name please used"
                                     "the skiprows and names arguments."
                                     "".format(col_name, pandas_df.columns))
        # 4.
        if "inst_flag" not in pandas_df.columns:
            pandas_df["inst_flag"] = 0
        # 5 and 6.
        if store:
            self._set_data(pandas_df)
            return self.get_data()
        else:
            return pandas_df

    def _set_data(self, data):
        """Store the data.
        ----
        Arguments:
            data : Unconstrained type but not None,
                Data loaded from the data file.
        """
        self.__data = data

    def get_data(self, **kwargs):
        """Return the data.
        ----
        Returns:
            Unconstrained type but not None, Data stored or loaded from the data file. Return None
                if no data stored and load-data method not implemented.
        """
        if not(self.is_data_stored()):
            try:
                return self.load_data(**kwargs)
            except:
                logger.warning("No data stored and method load_data failed to load datafile {}"
                               "\nprovided error: {}"
                               "".format(self.get_filename(),
                                         sys.exc_info()))

        return self.__data
