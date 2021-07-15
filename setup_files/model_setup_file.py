#!/usr/bin/python
# -*- coding:  utf-8 -*-
import lisa.posterior.core.model.manager_model as mgr
from lisa.posterior.exoplanet.model.gravgroup.model import GravGroup
from lisa.posterior.exoplanet.model.gravgroup_dynam.model import GravGroupDyn

manager = mgr.Manager_Model()

manager.add_available_model(GravGroup)
manager.add_available_model(GravGroupDyn)
