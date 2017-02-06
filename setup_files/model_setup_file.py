#!/usr/bin/python
# -*- coding:  utf-8 -*-
import source.posterior.core.model.manager_model as mgr
from source.posterior.exoplanet.model.gravgroup import GravGroup

manager = mgr.Manager_Model()

manager.add_available_model(GravGroup)
