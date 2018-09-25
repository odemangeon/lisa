#!/usr/bin/python
# -*- coding:  utf-8 -*-
"""
:py:mod:'limb_darkening.py' - Define Limb darkening paramcontainers.

This module contain all paramcontainers for all available parametrisation of the limb-darkening
available for different transit models.

@TODO:
"""

from logging import getLogger

from ...core.parameter import Parameter
from ...core.paramcontainer import Core_ParamContainer


## Logger object
logger = getLogger()


class CoreLD(Core_ParamContainer):
    """docstring for CoreLD."""

    __category__ = "LDs"
    __ld_type__ = None
    __ordered_paramname_list__ = None

    def __init__(self, star=None, name="", **kwargs):
        """docstring CoreLD init method.

        :param Star star: (default: None), Star to which the limb darkening refers too
        :param str name: (default: ""), Name of the Limb darkening param container (should not include the
            name of the star)

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        super(CoreLD, self).__init__(name=name, name_prefix=star.name, **kwargs)
        self.star = star

    @property
    def star(self):
        """Return the star instance the CoreLD object refers too."""
        return self.__star

    @star.setter
    def star(self, star):
        """Set the star attribute of a CoreLD."""
        if self.hasstar:
            logger.warning("The Star to which the CoreLD refers to has already been "
                           "defined. One should not redefined it so set_star command is "
                           "ignored")
        else:
            if star is None:
                logger.debug("No star provided for CoreLD {}.".format(self.get_name()))
            else:
                self.__star = star
                self.name.prefix = star.name
                logger.debug("star of CoreLD {} set to {}."
                             "".format(self.get_name(), star.get_name()))

    @property
    def ld_type(self):
        """Return a string giving the type of limb darkening parametrisation (eg: "quadratic")."""
        return self.__ld_type__

    @property
    def hasstar(self):
        """Indicate if a CoreLD instance has a attibute star defined."""
        if hasattr(self, "star"):
            return self.star is not None
        else:
            return False

    @property
    def init_LD_values(self):
        """Initial list of LD values for the initialisation of the batman model."""
        raise NotImplementedError("You should overwrite this property when you subclass CoreLD")

    def __get_list_all_paramnames(self):
        """Return the list of all parameters names."""
        if self.__ordered_paramname_list__ is None:
            raise ValueError("Can't use ordered=True if __ordered_paramname_list__ is not "
                             "defined")
        else:
            if (set(self.__ordered_paramname_list__) ==
               set(super(CoreLD, self).get_list_paramnames())):
                return self.__ordered_paramname_list__
            else:
                raise ValueError("__ordered_paramname_list__ doesn't contain all the "
                                 "parameters")

    def __get_list_all_params(self):
        """Return the list of all parameters."""
        return [self.parameters[paramname] for paramname in self.__get_list_all_paramnames()]


class LinearLD(CoreLD):
    """docstring for LinearLD."""

    __ld_type__ = "linear"
    __ordered_paramname_list__ = ["ldc1"]

    def __init__(self, star=None, name="", **kwargs):
        """docstring LinearLD init method.

        :param Star star: (default: None), Star to which the limb darkening refers too
        :param str name: (default: ""), Name of the Limb darkening param container (should not include the
            name of the star)

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        super(LinearLD, self).__init__(star=star, name=name, **kwargs)
        ## Radius of the planet
        self.add_parameter(Parameter(name="ldc1", name_prefix=self.name, main=False))

    @property
    def init_LD_values(self):
        return [0.5, ]


class QuadraticLD(CoreLD):
    """docstring for QuadraticLD."""

    __ld_type__ = "quadratic"
    __ordered_paramname_list__ = ["ldc1", "ldc2"]

    def __init__(self, star=None, name="", **kwargs):
        """docstring QuadraticLD init method.

        :param Star star: (default: None), Star to which the limb darkening refers too
        :param str name: (default: ""), Name of the Limb darkening param container (should not include the
            name of the star)

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        super(QuadraticLD, self).__init__(star=star, name=name, **kwargs)
        ## Radius of the planet
        self.add_parameter(Parameter(name="ldc1", name_prefix=self.name, main=False))
        self.add_parameter(Parameter(name="ldc2", name_prefix=self.name, main=False))

    @property
    def init_LD_values(self):
        return [0.4, 0.2]


class SquareRootLD(CoreLD):
    """docstring for SquareRootLD."""

    __ld_type__ = "squareroot"
    __ordered_paramname_list__ = ["ldc1", "ldc2"]

    def __init__(self, star=None, name="", **kwargs):
        """docstring SquareRootLD init method.

        :param Star star: (default: None), Star to which the limb darkening refers too
        :param str name: (default: ""), Name of the Limb darkening param container (should not include the
            name of the star)

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        super(SquareRootLD, self).__init__(star=star, name=name, **kwargs)
        ## Radius of the planet
        self.add_parameter(Parameter(name="ldc1", name_prefix=self.name, main=False))
        self.add_parameter(Parameter(name="ldc2", name_prefix=self.name, main=False))

    @property
    def init_LD_values(self):
        return [0.4, 0.2]


class LogarithmicLD(CoreLD):
    """docstring for LogarithmicLD."""

    __ld_type = "logarithmic"
    __ordered_paramname_list__ = ["ldc1", "ldc2"]

    def __init__(self, star=None, name="", **kwargs):
        """docstring LogarithmicLD init method.

        :param Star star: (default: None), Star to which the limb darkening refers too
        :param str name: (default: ""), Name of the Limb darkening param container (should not include the
            name of the star)

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        super(LogarithmicLD, self).__init__(star=star, name=name, **kwargs)
        ## Radius of the planet
        self.add_parameter(Parameter(name="ldc1", name_prefix=self.name, main=False))
        self.add_parameter(Parameter(name="ldc2", name_prefix=self.name, main=False))

    @property
    def init_LD_values(self):
        return [0.4, 0.2]


class ExponentialLD(CoreLD):
    """docstring for ExponentialLD."""

    __ld_type__ = "exponential"
    __ordered_paramname_list__ = ["ldc1", "ldc2"]

    def __init__(self, star=None, name="", **kwargs):
        """docstring ExponentialLD init method.

        :param Star star: (default: None), Star to which the limb darkening refers too
        :param str name: (default: ""), Name of the Limb darkening param container (should not include the
            name of the star)

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        super(SquareRootLD, self).__init__(star=star, name=name, **kwargs)
        ## Radius of the planet
        self.add_parameter(Parameter(name="ldc1", name_prefix=self.name, main=False))
        self.add_parameter(Parameter(name="ldc2", name_prefix=self.name, main=False))

    @property
    def init_LD_values(self):
        return [0.4, 0.2]


class NonLinearLD(CoreLD):
    """docstring for NonLinearLD."""

    __ld_type__ = "nonlinear"
    __ordered_paramname_list__ = ["ldc1", "ldc2", "ldc3", "ldc4"]

    def __init__(self, star=None, name="", **kwargs):
        """docstring NonLinearLD init method.

        :param Star star: (default: None), Star to which the limb darkening refers too
        :param str name: (default: ""), Name of the Limb darkening param container (should not include the
            name of the star)

        Keyword arguments are passed to Core_Paramcontainer.__init__ (see docstring for more info).
        Only name_prefix should not be provided as arguments, since it set automatically to gravgroup.name
        """
        super(NonLinearLD, self).__init__(star=star, name=name, **kwargs)
        ## Radius of the planet
        self.add_parameter(Parameter(name="ldc1", name_prefix=self.name, main=False))
        self.add_parameter(Parameter(name="ldc2", name_prefix=self.name, main=False))
        self.add_parameter(Parameter(name="ldc3", name_prefix=self.name, main=False))
        self.add_parameter(Parameter(name="ldc4", name_prefix=self.name, main=False))

    @property
    def init_LD_values(self):
        return [0.5, 0.1, 0.1, -0.1]


## Dictionary relating the LD model name to the LD param container class
dic_paramcont_class = {'linear': LinearLD,
                       'quadratic': QuadraticLD,
                       'squareroot': SquareRootLD,
                       'logarithmic': LogarithmicLD,
                       'exponential': ExponentialLD,
                       'nonlinear': NonLinearLD
                       }


class Manager_LD(object):
    """docstring for Manager_LD."""

    def get_LD_parcont_subclass(self, ld_mod_name):
        return dic_paramcont_class[ld_mod_name]
