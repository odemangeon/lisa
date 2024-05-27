from ..posterior.core.dataset_and_instrument.manager_dataset_instrument import Manager_Inst_Dataset
from ..posterior.core.dataset_and_instrument.instrument import Default_Instrument
from ..posterior.core.dataset_and_instrument.indicator import IND_Instrument, IND_Dataset
from ..posterior.core.dataset_and_instrument.indicator import HARPS_FWHM
from ..posterior.core.dataset_and_instrument.indicator import ESPRESSO_FWHM
from ..posterior.exoplanet.dataset_and_instrument.lc import LC_Instrument, LC_Dataset
from ..posterior.exoplanet.dataset_and_instrument.rv import RV_Instrument, RV_Dataset
# from ..posterior.exoplanet.dataset_and_instrument.ttv import TTV_Instrument, TTV_Dataset
from ..posterior.exoplanet.dataset_and_instrument.lc import K2, Kepler, CHEOPS, CoRoT
from ..posterior.exoplanet.dataset_and_instrument.rv import HARPS, SOPHIE_HE, SOPHIE_HR

manager = Manager_Inst_Dataset()

manager.define_def_instrument_class(Default_Instrument)

manager.add_available_inst_cat(LC_Instrument, LC_Dataset)
manager.add_available_inst_cat(RV_Instrument, RV_Dataset)
manager.add_available_inst_cat(IND_Instrument, IND_Dataset)

manager.add_available_inst(K2)
manager.add_available_inst(Kepler)
manager.add_available_inst(CHEOPS)
manager.add_available_inst(CoRoT)

manager.add_available_inst(HARPS)
manager.add_available_inst(SOPHIE_HE)
manager.add_available_inst(SOPHIE_HR)

manager.add_available_inst(HARPS_FWHM)
manager.add_available_inst(ESPRESSO_FWHM)
