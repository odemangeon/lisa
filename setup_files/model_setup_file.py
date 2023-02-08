#!/usr/bin/python
# -*- coding:  utf-8 -*-
import lisa.posterior.core.model.manager_model as mgr
from lisa.posterior.exoplanet.model.gravgroup.model import GravGroup
try:
    from lisa.posterior.exoplanet.model.gravgroup_dynam.model import GravGroupDyn
    gravgroupdyn_imported = True
except ImportError:
    gravgroupdyn_imported = False

manager = mgr.Manager_Model()

manager.add_available_model(GravGroup)
if gravgroupdyn_imported:
    manager.add_available_model(GravGroupDyn)
