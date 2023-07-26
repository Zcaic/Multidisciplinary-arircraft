import aerosandbox as asb
import aerosandbox.numpy as np
from aerosandbox.geometry.airfoil.airfoil import get_UIUC_coordinates

import logging

from utils.dotdict import DotDict

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

airfoils_list = DotDict(
    asb.Airfoil(name="rootaf", coordinates=get_UIUC_coordinates("rae2822")),
    asb.Airfoil(name="tipaf", coordinates=get_UIUC_coordinates("dae11")),
)

# print(airfoils_list)

wings_list = DotDict(
    asb.Wing(
        name="mainWing",
        xsecs=[
            asb.WingXSec(
                xyz_le=[0, 0, 0], chord=5.5, twist=0, airfoil=airfoils_list.rootaf
            ),
            asb.WingXSec(
                xyz_le=[2.5, 5, 0], chord=2.5, twist=0, airfoil=airfoils_list.rootaf
            ),
        ],
    ),
    asb.Wing(
        name="secondaryWing",
        xsecs=[
            asb.WingXSec(
                xyz_le=[0, 0, 0], chord=1, twist=0, airfoil=airfoils_list.tipaf
            ),
        ],
    ),
)

# print(airfoils_list.rootaf)
bwb = asb.Airplane(
    name="bwb",
    xyz_ref=[0, 0, 0],
    wings=[
       wings_list.mainWing,
    ],
)
bwb.draw()
