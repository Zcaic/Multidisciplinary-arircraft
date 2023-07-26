import aerosandbox as asb
import aerosandbox.numpy as np
from aerosandbox.geometry.airfoil.airfoil import get_UIUC_coordinates
from utils.dotdict import DotDict

airfoils_list = DotDict(
    rootaf=asb.Airfoil(name="rootaf", coordinates=get_UIUC_coordinates(name="rae2822")),
)

print(airfoils_list.keys())

wings_list = [
    asb.Wing(
        name="mainWing",
        xsecs=asb.WingXSec(
            xyz_le=[0, 0, 0], chord=5.5, twist=0, airfoil=airfoils_list.rootaf
        ),
    ),
]
