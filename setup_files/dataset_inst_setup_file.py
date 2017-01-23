#!/usr/bin/python
# -*- coding:  utf-8 -*-
import source.posterior.core.dataset_and_instrument.manager_dataset_instrument as mgr
from source.posterior.exoplanet.dataset_and_instrument.lc import LC_Instrument, LC_Dataset
from source.posterior.exoplanet.dataset_and_instrument.rv import RV_Instrument, RV_Dataset
from source.posterior.exoplanet.dataset_and_instrument.lc import K2, Kepler, CHEOPS, CoRoT
from source.posterior.exoplanet.dataset_and_instrument.rv import HARPS, SOPHIE_HE, SOPHIE_HR

manager = mgr.Manager_Inst_Dataset()

manager.set_dataset_for_inst_type(LC_Instrument.inst_type, LC_Dataset)
manager.set_dataset_for_inst_type(RV_Instrument.inst_type, RV_Dataset)

manager.add_available_inst(K2)
manager.add_available_inst(Kepler)
manager.add_available_inst(CHEOPS)
manager.add_available_inst(CoRoT)

manager.add_available_inst(HARPS)
manager.add_available_inst(SOPHIE_HE)
manager.add_available_inst(SOPHIE_HR)
