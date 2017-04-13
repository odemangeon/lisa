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

    __category__ = "limbdarkening"

    def __init__(self, star=None, name=""):
        super(CoreLD, self).__init__(name=name)
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
                logger.debug("No star provided for CoreLD {}.".format(self.name))
            else:
                self.__star = star
                self.name_prefix = star.name
                logger.debug("star of CoreLD {} set to {}."
                             "".format(self.name, star.name))

    @property
    def hasstar(self):
        """Indicate if a CoreLD instance has a attibute star defined."""
        if hasattr(self, "star"):
            return self.star is not None
        else:
            return False

class QuadraticLD(CoreLD):
    """docstring for QuadraticLD."""
    def __init__(self, star=None, name=""):
        super(QuadraticLD, self).__init__(star, name)
        
