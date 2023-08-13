import aerosandbox as asb
import aerosandbox.numpy as np
from aerosandbox.geometry.airfoil.airfoil import get_UIUC_coordinates

from utils.asb2cad import Asb2Cad

import logging
from typing import Dict

import casadi as ca

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


airfoils_list: Dict[str, asb.Airfoil] = dict(
    rae2822=asb.Airfoil(name="rea2822", coordinates=get_UIUC_coordinates("rae2822")),
    dae11=asb.Airfoil(name="dea11", coordinates=get_UIUC_coordinates("dae11")),
    naca0012=asb.Airfoil(name="naca0012"),
)
# print(airfoils_list)


fuse = asb.Fuselage(
    name="fuse",
    xsecs=[
        asb.FuselageXSec(xyz_c=[0, 0, 0.45], radius=0),
        asb.FuselageXSec(xyz_c=[4.31, 0.0, 0.60], width=1.21, height=1.38),
        asb.FuselageXSec(xyz_c=[6.05, 0, 0.60], width=1.38, height=1.38),
        asb.FuselageXSec(xyz_c=[9.28, 0, 0.49], width=1.95, height=1.18),
        asb.FuselageXSec(xyz_c=[15.06, 0, 0.49], width=1.0, height=1.02),
        asb.FuselageXSec(xyz_c=[16.107, 0, 0.49], radius=0.4),
        asb.FuselageXSec(xyz_c=[16.107, 0, 0.49], radius=0),
    ],
    analysis_specific_options={
        asb.AeroBuildup: dict(nose_fineness_ratio=3.6, E_wave_drag=2.5)
    },
)

MainWing = asb.Wing(
    name="MainWing",
    xsecs=[
        asb.WingXSec(
            xyz_le=[6.304, 0, 0.29], chord=5.61, airfoil=airfoils_list["rae2822"]
        ),
        asb.WingXSec(
            xyz_le=[6.304 + 5.05 * np.tand(41.06), 5.05, 0.29],
            chord=1.20,
            airfoil=airfoils_list["rae2822"],
        ),
    ],
    symmetric=True,
)

VstabWing = asb.Wing(
    name="VstabWing",
    xsecs=[
        asb.WingXSec(
            xyz_le=[9.783, 0, 0.85], chord=5.833, airfoil=airfoils_list["naca0012"]
        ),
        asb.WingXSec(
            xyz_le=[9.783 + 0.89 * np.tand(75.16), 0, 0.85 + 0.89],
            chord=2.88,
            airfoil=airfoils_list["naca0012"],
        ),
        asb.WingXSec(
            xyz_le=[
                9.783 + 0.89 * np.tand(75.16) + 2.246 * np.tand(49.67),
                0,
                0.85 + 0.89 + 2.246,
            ],
            chord=1.20,
            airfoil=airfoils_list["naca0012"],
        ),
    ],
)

HstabWing = asb.Wing(
    name="HstabWing",
    xsecs=[
        asb.WingXSec(
            xyz_le=[12.391, 0.5, 0.29], chord=3.57, airfoil=airfoils_list["naca0012"]
        ),
        asb.WingXSec(
            xyz_le=[12.391 + 2.53 * np.tand(41.49), 0.5 + 2.533, 0.29],
            chord=1.30,
            airfoil=airfoils_list["naca0012"],
        ),
    ],
    symmetric=True,
)

fighter = asb.Airplane(
    "fighter", wings=[MainWing, VstabWing, HstabWing], fuselages=[fuse]
)
fighter.draw()

ap = asb.AeroBuildup(
    airplane=fighter,
    op_point=asb.OperatingPoint(
        velocity=272.233829,
        alpha=1,
    ),
).run()

print(ap)
print(ap['CL']/ap["CD"])


# cad=Asb2Cad(fighter)
# cad.export_cadquery_geometry(filename='fighter.step',union=True)
