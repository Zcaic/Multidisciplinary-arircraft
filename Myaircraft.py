import aerosandbox as asb
import aerosandbox.numpy as np
from aerosandbox.geometry.airfoil.airfoil import get_UIUC_coordinates

import logging
from typing import Dict

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

airfoils_list:Dict[str,asb.Airfoil]= dict(
    rootaf=asb.Airfoil(name="rootaf", coordinates=get_UIUC_coordinates("rae2822")),
    tipaf=asb.Airfoil(name="tipaf", coordinates=get_UIUC_coordinates("dae11")),
)

ne=airfoils_list["rootaf"].get_aero_from_neuralfoil(alpha=2,Re=1e+6)
xf=asb.XFoil(airfoil=airfoils_list["rootaf"],Re=1e+6)

print(ne)
print(xf.alpha(2))
# print(airfoils_list)

wings_list:Dict[str,asb.Wing] = dict(
    mainWing=asb.Wing(
        name="mainWing",
        xsecs=[
            asb.WingXSec(
                xyz_le=[0, 0, 0], chord=5.5, twist=0, airfoil=airfoils_list["rootaf"]
            ),
            asb.WingXSec(
                xyz_le=[2.5, 5, 0], chord=2.5, twist=0, airfoil=airfoils_list["rootaf"]
            ),
        ],
    ),
    secondaryWing=asb.Wing(
        name="secondaryWing",
        xsecs=[
            asb.WingXSec(
                xyz_le=[0, 0, 0], chord=1, twist=0, airfoil=airfoils_list["tipaf"]
            ),
        ],
    ),
)

wings_list['mainWing'].draw()