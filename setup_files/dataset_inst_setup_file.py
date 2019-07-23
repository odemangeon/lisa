#!/usr/bin/python
# -*- coding:  utf-8 -*-
import lisa.posterior.core.dataset_and_instrument.manager_dataset_instrument as mgr
from source.posterior.core.dataset_and_instrument.instrument import Default_Instrument
from source.posterior.exoplanet.dataset_and_instrument.lc import LC_Instrument, LC_Dataset
from source.posterior.exoplanet.dataset_and_instrument.rv import RV_Instrument, RV_Dataset
from source.posterior.exoplanet.dataset_and_instrument.ttv import TTV_Instrument, TTV_Dataset
from source.posterior.exoplanet.dataset_and_instrument.lc import K2, Kepler, CHEOPS, CoRoT
from source.posterior.exoplanet.dataset_and_instrument.rv import HARPS, SOPHIE_HE, SOPHIE_HR

manager = mgr.Manager_Inst_Dataset()

manager.define_def_instrument_class(Default_Instrument)

manager.add_available_inst_category(LC_Instrument, LC_Dataset)
manager.add_available_inst_category(RV_Instrument, RV_Dataset)
manager.add_available_inst_category(TTV_Instrument, TTV_Dataset)

manager.add_available_inst(K2)
manager.add_available_inst(Kepler)
manager.add_available_inst(CHEOPS)
manager.add_available_inst(CoRoT)

manager.add_available_inst(HARPS)
manager.add_available_inst(SOPHIE_HE)
manager.add_available_inst(SOPHIE_HR)
