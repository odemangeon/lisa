#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
dataset module.

The objective of this package is to provides the core Dataset class to store
and manipulate the data.

@DONE:
    - Dataset.__init__: Doc an UT
    - Dataset.filepath: Doc and UT
    - Dataset.filename: Doc and UT
    - Dataset.instrument: Doc and UT
    - Dataset.objectname: Doc and UT
    - Dataset._rm_data: Doc and UT
    - Dataset.is_data_loaded: Doc and UT
    - Dataset.load_data: Doc
    - Dataset._set_data: Doc and UT
    - Dataset.get_data: Doc and UT

@TODO:
    - Dataset.load_data: UT
    - See if possible to transform data in a property.
"""
from logging import getLogger
from sys import exc_info
from pandas import read_table
from numpy import asarray

from ....tools.miscellaneous import get_filename_from_file_path
from ....tools.metaclasses import MandatoryReadOnlyAttr


## Logger
logger = getLogger()


class Core_Dataset(object, metaclass=MandatoryReadOnlyAttr):
    """docstring for the Dataset abstract class."""

    __mandatoryattrs__ = ["instrument_subclass", ]

    ## Mandatory columns: For this abstract data base there is None
    _mandatory_columns = []

    ## name of the data  and data error columns
    _data_name = "data"
    _data_err_name = "data_err"

    def __init__(self, file_path, instrument_instance):
        """Dataset init method FOR INHERITANCE PURPOSES (as Dataset is an abstract class).

        This __init__ does:
            1. Store the path of the data file
            2. Get the file name from the file path and interpret the file name into object name,
               instrument name and type and eventually number of the dataset
            3. Store the name of the object observed with the data
            4. Define the instrument used to take the data
            5. Set the number attribute (if several datasets from the same instrument)
            6. Initialise the data attribute
        Remarks:
            - There is no need to check for the existance of the data file because it's done by
              the Manager_Inst_Dataset class who triggers the creation of the dataset subclass
              instances
        ----
        Arguments:
            file_path           : string,
                Path of file which contains the data
            instrument_instance : Instance of a Subclass of Core_Instrument,
                Core_Instrument instance that describes the isntrument used to measure the data.
        Raises:
            NotImplementedError : 1 case,
                -If you try to instanciate Dataset directly.
        """
        super(Core_Dataset, self).__init__()
        # 1.
        self.__filepath = file_path
        # 2.
        self.__filename = get_filename_from_file_path(self.filepath)
        filename_info = self.interpret_data_filename(self.filename)
        logger.debug("Interpretation of the datafile name: {}".format(filename_info))
        # 3.
        self.__objectname = filename_info["object"]
        # 4.
        self.__instrument = instrument_instance
        # 6.
        if filename_info["number"] is None:
            self.__number = 0
        else:
            self.__number = int(filename_info["number"])
        # 5.
        self._rm_data()
        # Make Dataset an abstract class
        if type(self) is Core_Dataset:
            raise NotImplementedError("Core_Dataset should not be instanciated!")

    def __repr__(self):
        return "<{} {}:{}>".format(self.__class__.__name__, self.dataset_name, self.filepath)

    @property
    def filepath(self):
        """Get the path of the data file."""
        return self.__filepath

    @property
    def filename(self):
        """Get the name of the data file."""
        return self.__filename

    @property
    def dataset_name(self):
        """Get the name of the data file."""
        filename_info = self.interpret_data_filename(data_file_name=self.filename)
        if filename_info["inst_subcat"] is None:
            return "{}_{}_{}_{}".format(filename_info["inst_cat"], filename_info["object"],
                                        filename_info["inst_name"], filename_info["number"])
        else:
            return "{}-{}_{}_{}_{}".format(filename_info["inst_cat"], filename_info["inst_subcat"],
                                           filename_info["object"], filename_info["inst_name"], filename_info["number"])

    @property
    def instrument(self):
        """Return the instrument instance."""
        return self.__instrument

    @property
    def object_name(self):
        """Return the name of the object the data are about."""
        return self.__objectname

    @property
    def number(self):
        """Return the number of the dataset (if several dataset from the same instrument)."""
        return self.__number

    @classmethod
    def interpret_data_filename(cls, data_file_name, raise_error=True):
        """Interpret data file name.

        If the format of the data file name is recognized the function return a dictionnary (see
        Returns below) otherwise return None.

        Arguments
        ---------
        data_file_name : string
            Data file name. The format depends on wheter or not the instrument class associated to the
            dataset has sub categories or not.
        raise_error    : Boolean
            If True the function will raise an error if the format is not correct

        Returns
        -------
        result: dictionnary with the interpration of the filename which contains the following keys:
            - object : name of the object observed with the data
            - inst_cat : category of instrument used to take the data. e.g. "LC", "RV", ...
            - inst_subcat : sub category of instrument used to take the data. e.g. "FWHM", None is this instrument category doesn't have subcategories
            - inst_fullcat : full category of instrument used to take the data including or not the
                instrument sub category when needed.
            - inst_name : Name of the instrument used to take the data.
            - number : give the number of the data file if there is several data files of the
                same object observed with the same instrument
        """
        if cls.instrument_subclass.has_subcategories:
            filename_format = "instcat-instsubcat_target_instrument(_number).*"
        else:
            filename_format = "instcat_target_instrument(_number).*"
        cuts = data_file_name.split("_")   # List of fields that were separated by "_"
        cuts[-1] = cuts[-1].split(".")[0]  # Remove the extension
        cuts_cat = cuts[0].split("-")
        format_error = False
        if len(cuts) < 3 or len(cuts) > 4:
            format_error = True
        if cls.instrument_subclass.has_subcategories:
            if len(cuts_cat) != 2:
                format_error = True
        else:
            if len(cuts_cat) != 1:
                format_error = True
        if format_error:
            if raise_error:
                raise ValueError(f"Data file name not recognized. Should be in the format {filename_format}. Got {data_file_name}")
            else:
                return None
        result = {"object": cuts[1],
                  "inst_cat": cuts_cat[0],
                  "inst_name": cuts[2]}
        if cls.instrument_subclass.has_subcategories:
            result["inst_subcat"] = cuts_cat[-1]
            result["inst_fullcat"] = f"{result['inst_cat']}-{result['inst_subcat']}"
        else:
            result["inst_subcat"] = None
            result["inst_fullcat"] = result['inst_cat']
        if len(cuts) == 3:
            result["number"] = 0
        elif len(cuts) == 4:
            result["number"] = int(cuts[3])
        return result

    @classmethod
    def validate_dataset_filename(cls, data_file_name):
        """Validate the name of a datafile.

        Arguments
        ---------
        data_file_name: string
            Name of the dataset file.

        Returns
        -------
        valid : bool
            If True the dataset file name is valid.
        """
        filename_info = cls.interpret_data_filename(data_file_name=data_file_name, raise_error=False)
        if filename_info is None:
            return False
        return cls.instrument_subclass.validate_inst_cat(filename_info["inst_cat"])

    def _rm_data(self):
        """Remove data previously loaded or initialse the data attribute."""
        self.__data = None
        logger.info("Data attribute has been removed/initialise in dataset of {}."
                    "".format(self.filename))

    def is_data_stored(self):
        """Tell if data has been stored.
        ----
        Returns:
            True is data has been loaded, False otherwise.
        """
        return self.__data is not None

    def load_data(self, store=False,
                  delim_whitespace=True,
                  skip_rows=0,
                  comment="#",
                  names="mandatory",
                  index_col=None,
                  skip_blank_lines=True,
                  header=0,
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
        pandas_df = read_table(self.filepath,
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
            return self.get_datatable()
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

    def get_datatable(self, **kwargs):
        """Return the data table.
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
                               "".format(self.filename,
                                         exc_info()))

        return self.__data

    def get_data(self):
        """Return the data vector."""
        pandas_df = self.get_datatable()
        return asarray(pandas_df[self._data_name])

    def get_data_err(self):
        """Return the data vector."""
        pandas_df = self.get_datatable()
        return asarray(pandas_df[self._data_err_name])
